import sys
from pyspark.sql import SparkSession, functions, types

spark = SparkSession.builder.appName('reddit relative scores').getOrCreate()
spark.sparkContext.setLogLevel('WARN')

assert sys.version_info >= (3, 5) # make sure we have Python 3.5+
assert spark.version >= '2.3' # make sure we have Spark 2.3+

comments_schema = types.StructType([
    types.StructField('archived', types.BooleanType()),
    types.StructField('author', types.StringType()),
    types.StructField('author_flair_css_class', types.StringType()),
    types.StructField('author_flair_text', types.StringType()),
    types.StructField('body', types.StringType()),
    types.StructField('controversiality', types.LongType()),
    types.StructField('created_utc', types.StringType()),
    types.StructField('distinguished', types.StringType()),
    types.StructField('downs', types.LongType()),
    types.StructField('edited', types.StringType()),
    types.StructField('gilded', types.LongType()),
    types.StructField('id', types.StringType()),
    types.StructField('link_id', types.StringType()),
    types.StructField('name', types.StringType()),
    types.StructField('parent_id', types.StringType()),
    types.StructField('retrieved_on', types.LongType()),
    types.StructField('score', types.LongType()),
    types.StructField('score_hidden', types.BooleanType()),
    types.StructField('subreddit', types.StringType()),
    types.StructField('subreddit_id', types.StringType()),
    types.StructField('ups', types.LongType()),
    #types.StructField('year', types.IntegerType()),
    #types.StructField('month', types.IntegerType()),
])


def main(in_directory, out_directory):
    comments = spark.read.json(in_directory, schema=comments_schema)
    comments.cache()
    # TODO
    subreddits = comments.groupBy('subreddit').agg(functions.avg(comments['score']).alias('avgscore'))
    subreddits = subreddits.cache()
    #subreddits.show()
    subreddits = subreddits.filter(subreddits['avgscore'] > 0)
    subreddits.createOrReplaceTempView("SUB")
    comments.createOrReplaceTempView("COM")
    #subreddits.show()
    subreddits = spark.sql(
        'SELECT /*+ BROADCAST(s) */ c.author, c.score, c.subreddit, s.avgscore FROM COM c INNER JOIN SUB s ON c.subreddit == s.subreddit'
    )
    subreddits_auth = subreddits.withColumn('relative_score', subreddits['score'] / subreddits['avgscore'])
    #subreddits_auth.show()
    subreddits_max = subreddits_auth.groupby('subreddit').agg(functions.max('relative_score').alias('max_rel_score'))
    #subreddits_max.show()
    subreddits_max.createOrReplaceTempView("MAX")
    subreddits_auth.createOrReplaceTempView("AUT")
    subreddits = spark.sql(
        'SELECT /*+ BROADCAST(m, a) */ a.subreddit, a.author, m.max_rel_score FROM MAX m INNER JOIN AUT a ON m.subreddit == a.subreddit AND m.max_rel_score == a.relative_score'
    )
    #subreddits.show()
    subreddits.write.json(out_directory, mode='overwrite')


if __name__=='__main__':
    in_directory = sys.argv[1]
    out_directory = sys.argv[2]
    main(in_directory, out_directory)
