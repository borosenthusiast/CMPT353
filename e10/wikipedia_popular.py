import sys
from pyspark.sql import SparkSession, functions, types
import re

spark = SparkSession.builder.appName('wikipedia popular').getOrCreate()
spark.sparkContext.setLogLevel('WARN')

assert sys.version_info >= (3, 5) # make sure we have Python 3.5+
assert spark.version >= '2.3' # make sure we have Spark 2.3+

wiki_schema = types.StructType([
    types.StructField('language', types.StringType()),
    types.StructField('title', types.StringType()),
    types.StructField('requests', types.LongType()),
    types.StructField('bytes', types.LongType())
])

#adapted from examples in https://docs.python.org/3/library/re.html
def file2date(pathname):
    return re.search(r'([0-9]{8}\-[0-9]{2})', pathname).group(1)

def main(in_directory, out_directory):
    wikipedia = spark.read.csv(in_directory, schema=wiki_schema, sep=' ').withColumn('filename', functions.input_file_name())
    #wikipedia.show()
    wiki_clean = wikipedia.filter(wikipedia['language'] == 'en')
    wiki_clean = wiki_clean.filter(wiki_clean['title'] != 'Main_Page')
    wiki_clean = wiki_clean.filter(wiki_clean['title'].startswith('Special:') == False)
    f2d = functions.udf(lambda fp: file2date(fp), returnType=types.StringType())
    wiki_clean = wiki_clean.withColumn('date', f2d(wiki_clean['filename']))
    wiki_clean = wiki_clean.drop('language', 'bytes', 'filename')
    wiki_clean = wiki_clean.cache() #best results
    #wiki_clean.show()
    most_frequently_accessed = wiki_clean.groupBy('date')
    most_frequently_accessed = most_frequently_accessed.agg(functions.max(wiki_clean['requests']).alias('requests'))
    #most_frequently_accessed.cache()
    most_frequently_accessed = most_frequently_accessed.alias('a').join(wiki_clean.alias('b'), 
        (wiki_clean['requests'] == most_frequently_accessed['requests'])
        & (wiki_clean['date'] == most_frequently_accessed['date'])).select('a.date', 'b.title', 'a.requests')
    

    most_frequently_accessed = most_frequently_accessed.sort('date', 'title')
    #most_frequently_accessed.show()
    most_frequently_accessed.write.csv(out_directory + '-wikipedia', mode='overwrite')

if __name__=='__main__':
    in_directory = sys.argv[1]
    out_directory = sys.argv[2]
    main(in_directory, out_directory)
