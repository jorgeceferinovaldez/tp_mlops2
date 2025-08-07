# Guía del Pipeline de Experimentación - Clasificación de Estrellas

Esta guía describe el flujo completo para ejecutar un experimento de machine learning en el proyecto de clasificación de objetos estelares.

## Tabla de Contenidos
1. [Resumen del Pipeline](#resumen-del-pipeline)
2. [Prerequisitos](#prerequisitos)
3. [Paso 1: ETL - Procesamiento de Datos](#paso-1-etl---procesamiento-de-datos)
4. [Paso 2: Experimentación con MLflow](#paso-2-experimentación-con-mlflow)
5. [Paso 3: Re-entrenamiento del Modelo](#paso-3-re-entrenamiento-del-modelo)
6. [Verificación y Monitoreo](#verificación-y-monitoreo)
7. [Troubleshooting](#troubleshooting)

---

## Resumen del Pipeline

El pipeline de experimentación consta de **3 pasos principales**:

```
1. DAG ETL → 2. Notebook Experimentación → 3. DAG Re-entrenamiento
   ↓                    ↓                         ↓
Datos limpios      Mejor modelo            Modelo en producción
```

**Flujo completo:**
1. **ETL**: El DAG `process_etl_stellar_data` descarga, procesa y almacena los datos
2. **Experimentación**: La notebook `experiment_mlflow_randomforest.ipynb` encuentra el mejor modelo
3. **Re-entrenamiento**: El DAG `retrain_the_model` actualiza el modelo en producción

---

## Prerequisitos

### 1. Servicios Necesarios
Asegúrate de que los siguientes servicios estén ejecutándose:

```bash
# Iniciar todos los servicios necesarios
docker compose --profile all up -d

# Verificar que los servicios estén saludables
docker compose ps
```

### 2. Acceso a las Interfaces
- **Airflow**: http://localhost:8080 (airflow/airflow)
- **MLflow**: http://localhost:5000
- **MinIO**: http://localhost:9001 (minio/minio123)

### 3. Variables de Airflow
Verifica que las siguientes variables estén configuradas en Airflow:
- `target_col_star`: "class"
- `test_size_star`: 0.3

---

## Paso 1: ETL - Procesamiento de Datos

### Objetivo
Descargar el dataset SDSS17, procesarlo y guardarlo en el bucket de MinIO.

### Ejecución del DAG

1. **Accede a la interfaz de Airflow**: http://localhost:8080

2. **Busca el DAG**: `process_etl_stellar_data`

3. **Ejecuta el DAG**:
   - Haz clic en el DAG
   - Presiona "Trigger DAG"
   - Espera a que complete exitosamente (~5-10 minutos)

### Tareas del DAG
El DAG ejecuta las siguientes tareas en secuencia:

```
obtain_original_data → preprocess_data → split_dataset → standardize_data
```

1. **`obtain_original_data`**: Descarga el dataset desde Google Drive
2. **`preprocess_data`**: 
   - Codifica variables categóricas con LabelEncoder
   - Elimina la columna `rerun_ID`
   - Guarda metadatos en `data_star.json`
   - Registra el dataset en MLflow
3. **`split_dataset`**: Divide en train/test (70/30) con estratificación
4. **`standardize_data`**: 
   - Normaliza los datos usando StandardScaler
   - Guarda parámetros del scaler
   - Registra métricas en MLflow

### Verificación
Tras completarse exitosamente:
- **MinIO**: Verifica que existan los archivos en `s3://data/final/`
- **MLflow**: Revisa el experimento "Star Classification" con el run de ETL

---

## Paso 2: Experimentación con MLflow

### Objetivo
Encontrar el mejor modelo y hiperparámetros usando optimización bayesiana con Optuna.

### Ejecución de la Notebook

1. **Accede al directorio**: `notebook_example/`

2. **Configuración del entorno**:
   ```bash
   # Variables de entorno necesarias
   export AWS_ACCESS_KEY_ID=minio
   export AWS_SECRET_ACCESS_KEY=minio123
   export MLFLOW_S3_ENDPOINT_URL=http://localhost:9000
   export AWS_ENDPOINT_URL_S3=http://localhost:9000
   ```

3. **Ejecuta la notebook**: `experiment_mlflow_randomforest.ipynb`
   - Instala las dependencias si es necesario
   - Ejecuta todas las celdas secuencialmente
   - El proceso tomará ~5-10 minutos para entrenar el modelo Random Forest

### Proceso de Experimentación

La notebook realiza:

1. **Carga de datos** desde MinIO (train/test ya separados)
2. **Entrenamiento de Random Forest** con parámetros específicos:
   - n_estimators: 200
   - max_depth: 25
3. **Evaluación del modelo** en datos de entrenamiento y test:
   - Métricas: F1-score macro
   - Tracking automático en MLflow
4. **Registro del modelo** en desarrollo y producción
5. **Configuración del modelo productivo** con alias "champion"

### Modelo y Parámetros Utilizados

- **Random Forest**: 
  - `n_estimators`: 200 (número de árboles en el bosque)
  - `max_depth`: 25 (profundidad máxima de cada árbol)
  - Criterio: Gini (por defecto para clasificación)

### Verificación
- **MLflow**: Revisa el experimento "Star Classification" con el run del Random Forest
- **Modelo Registry**: Verifica que `star_class_model_prod` y `star_class_model_dev` estén registrados
- **Alias Champion**: Confirma que el modelo productivo tenga el alias "champion"

---

## Paso 3: Re-entrenamiento del Modelo

### Objetivo
Re-entrenar el modelo campeón con los datos más recientes y decidir si promoverlo a producción.

### Ejecución del DAG

1. **Accede a Airflow**: http://localhost:8080

2. **Busca el DAG**: `retrain_the_model`

3. **Ejecuta el DAG**:
   - Haz clic en el DAG
   - Presiona "Trigger DAG"
   - El proceso tomará ~5 minutos

### Tareas del DAG
El DAG ejecuta las siguientes tareas:

```
retrain_stellar_model → evaluate_champion_challenge
```

1. **`retrain_stellar_model`**:
   - Carga el modelo campeón actual
   - Clona y re-entrena con datos frescos
   - Calcula F1-score en test
   - Registra como modelo "star" (challenger)

2. **`evaluate_champion_challenge`**:
   - Compara champion vs challenger en test data
   - Si challenger > champion: promueve challenger a champion
   - Si no: elimina el challenger
   - Registra métricas de comparación en MLflow

### Verificación
- **MLflow**: Revisa las métricas de comparación en el experimento
- **Modelo Registry**: Verifica qué modelo tiene el alias "champion"

---

## Verificación y Monitoreo

### Estado de los Datos
```bash
# Verificar archivos en MinIO
docker exec -it minio mc ls s3/data/final/train/
docker exec -it minio mc ls s3/data/final/test/
```

### Estado de MLflow
- **Experimentos**: http://localhost:5000
  - "Star Classification": Runs de ETL y comparación
  - "Star classification models": Runs de experimentación
- **Modelo Registry**: `star_class_model_prod` con versiones y aliases

### Logs de los DAGs
```bash
# Ver logs del DAG de ETL
docker compose logs airflow_scheduler | grep process_etl_stellar_data

# Ver logs del DAG de reentrenamiento  
docker compose logs airflow_scheduler | grep retrain_the_model
```

---

## Troubleshooting

### Problemas Comunes

#### ❌ DAG no aparece en Airflow
```bash
# Reiniciar scheduler
docker compose restart airflow_scheduler
# Verificar sintaxis del DAG
docker exec airflow_scheduler python -m py_compile /opt/airflow/dags/etl_process_grupal.py
```

#### ❌ Error de conexión a MinIO
```bash
# Verificar que MinIO esté corriendo
docker compose ps s3
# Recrear buckets si es necesario
docker compose up create_s3_buckets
```

#### ❌ Error en la notebook
```bash
# Verificar variables de entorno
echo $AWS_ACCESS_KEY_ID
echo $MLFLOW_S3_ENDPOINT_URL
# Reinstalar dependencias
pip install -r notebook_example/requirements.txt
```

#### ❌ Modelo no se encuentra en MLflow
- Verifica que el experimento "Star Classification" existe
- Asegúrate de que la notebook se ejecutó completamente
- Revisa el Model Registry para el modelo `star_class_model_prod`

### Limpieza y Reset

```bash
# Limpiar todos los experimentos (⚠️ DESTRUCTIVO)
# Acceder a MLflow UI y eliminar experimentos manualmente

# Limpiar buckets de MinIO
docker exec -it minio mc rm --recursive s3/data/
docker exec -it minio mc rm --recursive s3/mlflow/

# Reiniciar servicios
docker compose down
docker compose --profile all up -d
```

---

## Resumen de Archivos Importantes

| Archivo | Propósito |
|---------|-----------|
| `airflow/dags/etl_process_grupal.py` | DAG de ETL y preprocesamiento |
| `airflow/dags/retrain_the_model.py` | DAG de re-entrenamiento |
| `notebook_example/experiment_mlflow_randomforest.ipynb` | Experimentación con Random Forest |
| `notebook_example/mlflow_aux.py` | Utilidades para MLflow |
| `notebook_example/optuna_aux.py` | Funciones objetivo para Optuna |
| `docker-compose.yaml` | Orquestación de servicios |

---

**Notas importantes:**
- Los experimentos se ejecutan de forma secuencial: ETL → Notebook → Re-entrenamiento
- Cada paso depende del anterior para funcionar correctamente
- El modelo Random Forest se entrena con parámetros fijos (no optimización automática)
- Los modelos se versionan automáticamente en MLflow Model Registry
- El sistema registra el modelo entrenado tanto en desarrollo como en producción

Para dudas adicionales, consulta el `README.md` o `API_USAGE_GUIDE.md`.