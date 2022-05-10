from distutils.spawn import spawn
import glob
import os
import sys
import time
import numpy as np
import cv2

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla
import random

actor_list = []
IM_WIDTH = 640
IM_HEIGHT = 480

def process_img(image):
    i = np.array(image.raw_data)
    # print(i.shape)
    i2 = i.reshape((IM_HEIGHT, IM_WIDTH, 4))
    i3 = i2[:,:,:3]
    cv2.imshow("sensor", i3)
    cv2.waitKey(1)
    # print(i3)
    return i3/255.0

    # print(dir(image))
def main():
    try:
        client = carla.Client('localhost', 2000)
        client.set_timeout(2.0)

        world = client.get_world()
        blueprint_library = world.get_blueprint_library()

        bp = blueprint_library.filter("model3")[0]
        print(bp)

        spawn_point = random.choice(world.get_map().get_spawn_points())
        vehicle = world.spawn_actor(bp, spawn_point)
        vehicle.set_autopilot(True)
        vehicle.apply_control(carla.VehicleControl(throttle=1.0, steer=0.0))
        actor_list.append(vehicle)

        cam_bp = blueprint_library.find('sensor.camera.rgb')
        cam_bp.set_attribute("image_size_x", f"{IM_WIDTH}")
        cam_bp.set_attribute("image_size_y", f"{IM_HEIGHT}")
        cam_bp.set_attribute("fov", "110")
        

        spawn_point = carla.Transform(carla.Location(x=2.5, z=0.7))
        sensor = world.spawn_actor(cam_bp, spawn_point, attach_to=vehicle)

        actor_list.append(sensor)
        sensor.listen(lambda data: process_img(data))

        # sensor.listen(lambda image: image.save_to_disk('output/%06d.png' % image.frame))
        time.sleep(30)


    finally:
        for i in range(len(actor_list)):
            print(i, actor_list[i])
        
        time.sleep(10)
        print("destroying actors")
        for actor in actor_list:
            actor.destroy()

        print('done')


if __name__ == '__main__':
    main()