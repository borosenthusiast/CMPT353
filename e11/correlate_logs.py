import sys
import numpy as np
from pyspark.sql import SparkSession, functions, types, Row
import re

spark = SparkSession.builder.appName('correlate logs').getOrCreate()
spark.sparkContext.setLogLevel('WARN')

assert sys.version_info >= (3, 5) # make sure we have Python 3.5+
assert spark.version >= '2.3' # make sure we have Spark 2.3+

line_re = re.compile(r"^(\S+) - - \[\S+ [+-]\d+\] \"[A-Z]+ \S+ HTTP/\d\.\d\" \d+ (\d+)$")


def line_to_row(line):
    """
    Take a logfile line and return a Row object with hostname and bytes transferred. Return None if regex doesn't match.
    """
    m = line_re.match(line)
    if m:
        # TODO
        return Row(hostname=m.group(1), bytes=m.group(2))
    else:
        return None


def not_none(row):
    """
    Is this None? Hint: .filter() with it.
    """
    return row is not None


def create_row_rdd(in_directory):
    log_lines = spark.sparkContext.textFile(in_directory)
    # TODO: return an RDD of Row() objects
    row = log_lines.map(line_to_row)
    return row.filter(not_none)


def main(in_directory):
    logs = spark.createDataFrame(create_row_rdd(in_directory)).cache()
    #logs.show()
    # TODO: calculate r.
    count_requests = logs.groupby('hostname').count()
    #count_requests.show()
    sum_bytes = logs.groupby('hostname').agg(functions.sum('bytes').alias('sum_bytes')).cache()
    #sum_bytes.show()
    
    #print(n_values)
    count_requests.createOrReplaceTempView("REQ")
    sum_bytes.createOrReplaceTempView("SUM")
    data_points = spark.sql(
        'SELECT s.hostname, r.count AS request_count, s.sum_bytes FROM SUM s INNER JOIN REQ r ON s.hostname == r.hostname'
    )
    #data_points.show()
    data_points.cache()
    data_points = data_points.withColumn('request_count * sum_bytes', data_points['request_count'] * data_points['sum_bytes'])
    data_points = data_points.withColumn('request_count^2', data_points['request_count'] * data_points['request_count'])
    data_points = data_points.withColumn('sum_bytes^2', data_points['sum_bytes'] * data_points['sum_bytes'])
    #data_points.show()
    sum_data = data_points.groupby().agg(functions.sum('request_count').alias('sxi'), functions.sum('sum_bytes').alias('syi'),
        functions.sum('request_count * sum_bytes').alias('sxiyi'), functions.sum('request_count^2').alias('sxi2'), functions.sum('sum_bytes^2').alias('syi2'))
    #print(sum_data.first())
    n_values = sum_bytes.count()
    sum_xi = sum_data.first()[0]
    sum_yi = sum_data.first()[1]
    sum_xiyi = sum_data.first()[2]
    sum_xi_2 = sum_data.first()[3]
    sum_yi_2 = sum_data.first()[4]



    r = ((n_values * sum_xiyi) - (sum_xi * sum_yi)) / (np.sqrt((n_values * sum_xi_2) - (sum_xi)**2) * np.sqrt((n_values * sum_yi_2) - (sum_yi)**2)) # TODO: it isn't zero.
    print("r = %g\nr^2 = %g" % (r, r**2))


if __name__=='__main__':
    in_directory = sys.argv[1]
    main(in_directory)
