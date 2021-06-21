import string, re
import sys
from pyspark.sql import SparkSession, functions, types
from pyspark.sql.functions import split
from pyspark.sql.functions import explode
from pyspark.sql.functions import lower, col, desc

spark = SparkSession.builder.appName('wordcount').getOrCreate()
spark.sparkContext.setLogLevel('WARN')

assert sys.version_info >= (3, 5) # make sure we have Python 3.5+
assert spark.version >= '2.3' # make sure we have Spark 2.3+


def main(in_directory, out_directory):
    text = spark.read.text(in_directory).cache()
    text = text.withColumn("value", split("value", r'[%s\s]+' % (re.escape(string.punctuation),)))
    text = text.select(explode(text.value).alias('word'))
    text = text.select(lower(col('word')).alias('word'))
    text = text.filter(text['word'] != '')
    text = text.groupby('word').agg(functions.count('word').alias('count')).orderBy(desc("count"), "word")
    #text.show()
    text.write.csv(out_directory, mode='overwrite')
  

if __name__=='__main__':
    in_directory = sys.argv[1]
    out_directory = sys.argv[2]
    main(in_directory, out_directory)
