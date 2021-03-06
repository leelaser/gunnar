'''
Created on Dec 11, 2016

@author: tsbertalan
'''
import rospy
from std_msgs.msg import Float32
from geometry_msgs.msg import Point, Quaternion, TransformStamped
import tf

import numpy as np

from gunnar.motor import Motor

from __init__ import ROSNode


class ResettableRate(rospy.Rate):
    
    def reset(self):
        self.last_time = rospy.rostime.get_rostime()
        
    def remainingSeconds(self):
        return self.remaining().to_sec()
    
    def past(self):
        return self.remainingSeconds() <= 0

    
class Gunnar(object):
    def __init__(self):
        self._spds = [0, 0]
        
        self.robotSpeedsStr = ''
        self.speedSetRate = ResettableRate(rospy.get_param("~rate", 10))
        self.motors = [
                       Motor(35, 33, 31),
                       Motor(19, 23, 21),
                       ]
        
    def stop(self):
        self.spds = [0, 0]

    @property
    def spds(self):
        return list(self._spds)

    @spds.setter
    def spds(self, twoList):
        self._spds = list(twoList)
        
        if self.speedSetRate.past():
            changed = False
            for i in 0, 1:
                if twoList[i] != self.spds[i]:
                    self._spds[i] = twoList[i]
                    changed = True
            if changed:
                self.speedSetRate.reset()
                self.robotSpeedsStr = "(%.1f, %.1f)." % tuple(self.spds)

    def updateLidarAngleTf(self):
        if not hasattr(self, 'lidarAngleTfBroadcaster'):
            self.lidarAngleTfBroadcaster = tf.TransformBroadcaster()
        tfb = self.lidarAngleTfBroadcaster
        lidarAngle = self.lidarAngle
        tfb.sendTransform(
            (0, 0, 0),
            tf.transformations.quaternion_from_euler(0, 0, lidarAngle),
            rospy.Time.now(),
            'lidar',
            'base_link',                                   
            )
        
    @property
    def lidarAngle(self):
        return float(rospy.get_param('~lidarAngle', np.pi))

    def spinOnce(self):
        self.updateLidarAngleTf()
        
        
class VtargetListener(Gunnar, ROSNode):
    
    def __init__(self):
        super(VtargetListener, self).__init__()
        rospy.loginfo('Begin VtargetListener init.')
        rospy.Subscriber('/lwheel_vtarget', Float32, self.lwheelCallback)
        rospy.Subscriber('/rwheel_vtarget', Float32, self.rwheelCallback)
        rospy.loginfo('Done with VtargetListener init.')
        print 'Done with VtargetListener init.'
        
    def lwheelCallback(self, data):
        self.spds = [data.data, self.spds[1]]
        self.motors[0].setFrac(data.data)
        
    def rwheelCallback(self, data):
        self.spds = [self.spds[0], data.data]
        self.motors[1].setFrac(data.data)
        
    def main(self):
        r = rospy.Rate(rospy.get_param("~rate", 10))
        while not rospy.is_shutdown():
            # Time per loop iteration will be max(ts, tr, ti), where ts, tr,
            # and ti are the duration of the spin code, rate period, and idle
            # period, respectively. That is, the period will strive to match the
            # slower of the two Rates, but might be a longer if the spin takes
            # longer.
            #
            # This doesn't clarify why an idle is useful, rather than just using
            # a slower rate.
            self.spinOnce()
            r.sleep()
