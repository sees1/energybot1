import rospy
from sensor_msgs.msg import Imu
from geometry_msgs.msg import Vector3, Quaternion
from tf.transformations import quaternion_from_euler, quaternion_multiply
import tf
import serial

g=9.80665
PI = 3.14159
timeout=0.2

DEBUG=False

def send(ser, command : str, delay=timeout):
    ser.write(bytes.fromhex(command)) #Accelerometer Calibration
    rospy.sleep(delay)

class wt901:
    def __init__(self):
        rospy.init_node('wt901_node')
        self.device = rospy.get_param("wt901/port")
        self.orientation_covariance = rospy.get_param("wt901/orientation_covariance")
        self.linear_acceleration_covariance = rospy.get_param("wt901/linear_acceleration_covariance")
        self.angular_velocity_covariance = rospy.get_param("wt901/angular_velocity_covariance")

        self.ser = serial.Serial(self.device, 115200, timeout=None)
        if self.ser:
            rospy.loginfo(f"Successfully connected to {self.device}. Waiting for {timeout} sec")
            rospy.sleep(timeout)
        else:
            rospy.logerr("Can not connect to IMU!")
            exit(1)

        rospy.loginfo(f"Publishing to /imu/data")
        self.pub_imu = rospy.Publisher('/imu/data', Imu, queue_size=1)
        self.odom_broadcaster = tf.TransformBroadcaster()

    def update(self):
        imu = Imu()

        imu.angular_velocity_covariance = [-1, 0, 0, 0, 0, 0, 0, 0, 0]
        imu.linear_acceleration_covariance = [-1, 0, 0, 0, 0, 0, 0, 0, 0]
        imu.orientation_covariance = [-1, 0, 0, 0, 0, 0, 0, 0, 0]

        while True:
            # send(self.ser, 'FF AA 27 51 00', 0)
            data = self.ser.read(2)
            if data[1] == bytes.fromhex('61')[0]:
                data = self.ser.read(18)

                if DEBUG:
                    rospy.loginfo(f"Received {len(data)} bytes")
                    rospy.loginfo(''.join('{:02X} '.format(a) for a in data))

                axL,axH,ayL,ayH,azL,azH,wxL,wxH,wyL,wyH,wzL,wzH,RollL,RollH,PitchL,PitchH,YawL,YawH = data[:]

                ax=int.from_bytes([axH, axL], byteorder="big", signed=True)/32768*16*g
                ay=int.from_bytes([ayH, ayL], byteorder="big", signed=True)/32768*16*g
                az=int.from_bytes([azH, azL], byteorder="big", signed=True)/32768*16*g

                wx=int.from_bytes([wxH, wxL], byteorder="big", signed=True)/32768*2000/180*PI
                wy=int.from_bytes([wyH, wyL], byteorder="big", signed=True)/32768*2000/180*PI
                wz=int.from_bytes([wzH, wzL], byteorder="big", signed=True)/32768*2000/180*PI

                Roll=int.from_bytes([RollH, RollL], byteorder="big", signed=True)/32768*PI
                Pitch=int.from_bytes([PitchH, PitchL], byteorder="big", signed=True)/32768*PI
                Yaw=int.from_bytes([YawH, YawL], byteorder="big", signed=True)/32768*PI

                if DEBUG:
                    rospy.loginfo("Acceleration is: {:.2f} {:.2f} {:.2f}".format(ax, ay, az))
                    rospy.loginfo("Angular is: {:.2f} {:.2f} {:.2f}".format(wx, wy, wz))
                    rospy.loginfo("Angle is: {:.2f} {:.2f} {:.2f}".format(Roll, Pitch, Yaw))

                imu.angular_velocity = Vector3(wx, -wy, -wz)

                imu.angular_velocity_covariance = self.angular_velocity_covariance 
                # imu.angular_velocity_covariance = [
                #     0.0663,0,0,
                #     0, 0.1453, 0,
                #     0, 0, 0.0378
                # ]
                
                az-=2*g

                imu.linear_acceleration = Vector3(ax, -ay, -az)
                imu.linear_acceleration_covariance = self.linear_acceleration_covariance
                # imu.linear_acceleration_covariance = [
                #     0.0364, 0, 0,
                #     0, 0.0048, 0,
                #     0, 0, 0.0796
                # ]
                q = quaternion_from_euler(Roll, -Pitch, -Yaw)

                # self.odom_broadcaster.sendTransform(
                #         (0, 0, 0.),
                #         q,
                #         rospy.Time.now(),
                #         "imu",
                #         "map")
                                      
                # q_rot = quaternion_from_euler(PI, PI, 0)
                # q_res = quaternion_multiply(q_rot, q)
                
                imu.orientation = Quaternion(q[0], q[1], q[2], q[3])
                imu.orientation_covariance = self.orientation_covariance
                # imu.orientation_covariance = [
                #     0.0479, 0, 0,
                #     0, 0.0207, 0,
                #     0, 0, 0.0041
                # ]
            else:
                continue

            if imu.angular_velocity_covariance[0] == -1:
                continue

            imu.header.stamp = rospy.Time.now()
            imu.header.frame_id = "imu"
            
            self.pub_imu.publish(imu)
            return


if __name__ == '__main__':
    node = wt901()
    try:
        while not rospy.is_shutdown():
            node.update()
    except rospy.ROSInterruptException:
        pass
    node.ser.close()
    