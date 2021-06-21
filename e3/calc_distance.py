import pandas as pd
import numpy as np
import xml.etree.ElementTree as etree
import sys
import math
from pykalman import KalmanFilter

def output_gpx(points, output_filename):
    """
    Output a GPX file with latitude and longitude from the points DataFrame.
    """
    from xml.dom.minidom import getDOMImplementation
    def append_trkpt(pt, trkseg, doc):
        trkpt = doc.createElement('trkpt')
        trkpt.setAttribute('lat', '%.8f' % (pt['lat']))
        trkpt.setAttribute('lon', '%.8f' % (pt['lon']))
        trkseg.appendChild(trkpt)
    
    doc = getDOMImplementation().createDocument(None, 'gpx', None)
    trk = doc.createElement('trk')
    doc.documentElement.appendChild(trk)
    trkseg = doc.createElement('trkseg')
    trk.appendChild(trkseg)
    
    points.apply(append_trkpt, axis=1, trkseg=trkseg, doc=doc)
    
    with open(output_filename, 'w') as fh:
        doc.writexml(fh, indent=' ')

# XML -> dataframe adapted from https://stackoverflow.com/questions/41795198/more-efficient-conversion-of-xml-file-into-dataframe and the hint iter('{http://www.topografix.com/GPX/1/0}trkpt')
def get_data(gpx_file):
    xmlfile = etree.parse(gpx_file)
    kalman_data = []
    for d in xmlfile.iter('{http://www.topografix.com/GPX/1/0}trkpt'):
        kalman_data.append(d.attrib)
    df = pd.DataFrame(kalman_data).astype('float64')
    #print(df)
    return df

# Formula derived from https://stackoverflow.com/questions/27928/calculate-distance-between-two-latitude-longitude-points-haversine-formula/21623206
def haversine(lat1,lon1,lat2,lon2):
    earth = 6371
    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = (math.sin(dlat/2) ** 2) + (math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * (math.sin(dlon/2) ** 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return earth * c

def distance(df):
    df['lat2'] = df['lat'].shift()
    df['lon2'] = df['lon'].shift()
    df['haversine_distance'] = df.apply(lambda x: haversine(x['lat'], x['lon'], x['lat2'], x['lon2']), axis=1)
    #print(df)
    df2 = df['haversine_distance'].dropna()
    #print(df2)
    dist = sum(df2)
    #print(dist)
    return dist * 1000

def smooth(kalman_data):
    initial_state = kalman_data.iloc[0]
    observation_covariance = np.diag([0.00025, 0.00025]) ** 2
    transition_covariance = np.diag([0.0001, 0.0001]) ** 2
    kf = KalmanFilter(
        initial_state_mean=initial_state, 
        initial_state_covariance=observation_covariance,
        observation_covariance=observation_covariance, 
        transition_covariance=transition_covariance)
    kalman_smoothed, _ = kf.smooth(kalman_data)
    smoothed_data = pd.DataFrame(kalman_smoothed)
    smoothed_data.columns = ['lat', 'lon']
    return smoothed_data

def main():
    points = get_data(sys.argv[1])
    ### TEST CODE!!
    #points = get_data('walk1.gpx')
    ###-----------

    distance(points)
    print('Unfiltered distance: %0.2f' % (distance(points),))
    points = get_data(sys.argv[1])
    ### TEST CODE!!
    #points = get_data('walk1.gpx')
    ###-----------
    smoothed_points = smooth(points)
    print('Filtered distance: %0.2f' % (distance(smoothed_points),))
    output_gpx(smoothed_points, 'out.gpx')


if __name__ == '__main__':
    main()