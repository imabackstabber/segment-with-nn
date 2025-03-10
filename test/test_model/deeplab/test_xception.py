# coding=utf-8
''' test case for deeplab layers
'''
import tensorflow as tf
from segelectri.model.deeplab.xception.xception import Xception


class TestDeeplabLayers(tf.test.TestCase):
    def test_xception_with_input_layer(self):
        fake_input = tf.keras.Input((512, 512, 3), dtype=tf.float32)
        xlayer = Xception()
        outputs, skip = xlayer(fake_input)
        self.assertAllEqual(outputs.shape, [None, 64, 64, 2048])
        self.assertAllEqual(skip.shape, [None, 128, 128, 256])

    def test_xception_with_real_input(self):
        fake_input = tf.random.uniform((1, 512, 512, 3),
                                       minval=0,
                                       maxval=1,
                                       dtype=tf.float32)
        xlayer = Xception()
        outputs, skip = xlayer(fake_input)
        self.assertAllEqual(outputs.shape, [1, 64, 64, 2048])
        self.assertAllEqual(skip.shape, [1, 128, 128, 256])
