import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql import functions as F

## @params: [JOB_NAME]

try:
    sc = SparkContext()
    glueContext = GlueContext(sc)
    spark = glueContext.spark_session
    job = Job(glueContext)
except Exception as e:
    print(f"Initalizing Glue failed: {e}")
    raise

try:
    args = getResolvedOptions(sys.argv, ['JOB_NAME', 'GLUE_DB', 'GLUE_TABLE', 'SOURCE_PATH', 'TARGET_PATH'])
    source_path = args['SOURCE_PATH']
    target_path = args['TARGET_PATH']
    job_name = args['JOB_NAME']
    glue_db = args['GLUE_DB']
    glue_tbl = args['GLUE_TABLE']
    job.init(job_name, args)
except Exception as e:
    print(f"Initalizing job failed")
    raise
'''
try:
    print("creating dataframe from catalog")
    flight_data = glueContext.create_dynamic_frame.from_catalog(database = glue_db, table_name = glue_tbl, format = "json")
    print(f"print schema: ")
    data_frame = flight_data.toDF()
    df_pd = data_frame.toPandas()
    print(df_pd)
    print("data read successfully")
except Exception as e:
    print(f"error : {e}")
'''
try:
   
    df = spark.read.json(source_path, multiLine=True)
    
    # --------------------------------------------------------------------
    # 2. FLATTEN THE STRUCTURE
    # --------------------------------------------------------------------
    df_flat = df.select(
        "flight_date",
        "flight_status",
    
        # Departure fields
        F.col("departure.airport").alias("dep_airport"),
        F.col("departure.timezone").alias("dep_timezone"),
        F.col("departure.iata").alias("dep_iata"),
        F.col("departure.icao").alias("dep_icao"),
        F.col("departure.terminal").alias("dep_terminal"),
        F.col("departure.gate").alias("dep_gate"),
        F.col("departure.delay").alias("dep_delay"),
        F.col("departure.scheduled").alias("dep_scheduled"),
        F.col("departure.estimated").alias("dep_estimated"),
        F.col("departure.actual").alias("dep_actual"),
    
        # Arrival fields
        F.col("arrival.airport").alias("arr_airport"),
        F.col("arrival.timezone").alias("arr_timezone"),
        F.col("arrival.iata").alias("arr_iata"),
        F.col("arrival.icao").alias("arr_icao"),
        F.col("arrival.terminal").alias("arr_terminal"),
        F.col("arrival.gate").alias("arr_gate"),
        F.col("arrival.baggage").alias("arr_baggage"),
        F.col("arrival.scheduled").alias("arr_scheduled"),
        F.col("arrival.estimated").alias("arr_estimated"),
        F.col("arrival.actual").alias("arr_actual"),
    
        # Airline fields
        F.col("airline.name").alias("airline_name"),
        F.col("airline.iata").alias("airline_iata"),
        F.col("airline.icao").alias("airline_icao"),
    
        # Flight fields
        F.col("flight.number").alias("flight_number"),
        F.col("flight.iata").alias("flight_iata"),
        F.col("flight.icao").alias("flight_icao"),
    
        # Codeshared info (may be null)
        F.col("flight.codeshared.airline_name").alias("codeshared_airline_name"),
        F.col("flight.codeshared.airline_iata").alias("codeshared_airline_iata"),
        F.col("flight.codeshared.airline_icao").alias("codeshared_airline_icao"),
        F.col("flight.codeshared.flight_number").alias("codeshared_flight_number"),
        F.col("flight.codeshared.flight_iata").alias("codeshared_flight_iata"),
        F.col("flight.codeshared.flight_icao").alias("codeshared_flight_icao"),
    )
    
    # --------------------------------------------------------------------
    # 3. WRITE OUTPUT AS PARQUET TO S3
    # --------------------------------------------------------------------
    df_flat.write.mode("overwrite").parquet(target_path)
except Exception as e:
    print(f"Creating table from json failed: {e}")

try:
    print("Finalising the Glue job")
    job.commit()
except Exception as e:
    print(f"Error commiting Glue job: {e}")
    raise
    