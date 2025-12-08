def thruster_mix(pitch, roll, yaw, throttle):

    G = 0.8  # gain

    # forward/back (pitch)
    m1 = + pitch * G
    m2 = + pitch * G
    m3 = + pitch * G
    m4 = + pitch * G

    # roll (left/right)
    m1 += + roll * G
    m4 += + roll * G
    m2 -= + roll * G
    m3 -= + roll * G

    # yaw (rotate)
    m1 += + yaw
    m3 += + yaw
    m5 = + yaw
    m2 -= + yaw
    m4 -= + yaw
    m6 = - yaw

    # vertical
    m7 = throttle
    m8 = throttle

    motors = [m1, m2, m3, m4, m5, m6, m7, m8]

    motors = [max(min(x, 1), -1) for x in motors]
    return motors
