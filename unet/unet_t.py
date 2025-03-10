import tensorflow as tf
from tensorflow import keras


class downsamp_conv(keras.layers.Layer):
    def __init__(self, filters_num=128, **kwargs):
        """Initialize 'downsamp_conv'
        Args:
            filters_num:num of filters in corresponding layer when downsampling
        """
        super(downsamp_conv, self).__init__(**kwargs)

        self.filters_num = filters_num

    def build(self, input_shape):
        self.shape = input_shape

        self.conv_seq = keras.Sequential([
            keras.layers.Conv2D(filters=self.filters_num,
                                kernel_size=(3, 3),
                                padding='same'),
            keras.layers.Conv2D(filters=self.filters_num,
                                kernel_size=(3, 3),
                                padding='same')
        ])

    def call(self, inputs):
        output = self.conv_seq(inputs)
        return output

    # def get_config(self):


class upsamp_conv(keras.layers.Layer):
    def __init__(self, filters_num=128, **kwargs):
        """Initialize 'upsamp_conv'
        Args:
            filters_num:num of filter in corresponding layer
        """
        super(upsamp_conv, self).__init__(**kwargs)

        self.filters_num = filters_num

    def build(self, input_shape):
        self.shape = input_shape

        self.upsample_seq = keras.Sequential([
            keras.layers.Conv2D(filters=self.filters_num,
                                kernel_size=(3, 3),
                                padding='same'),
            keras.layers.Conv2D(filters=self.filters_num,
                                kernel_size=(3, 3),
                                padding='same'),
            keras.layers.UpSampling2D(size=(2, 2), interpolation='bilinear'),
            keras.layers.Conv2D(filters = self.filters_num//2,
                                kernel_size = (2,2),
                                padding='same')
        ])

    def call(self, inputs):
        output = self.upsample_seq(inputs)
        return output

    # def get_config(self):


class Unet(keras.layers.Layer):
    def __init__(self, min_kernel_num=64, num_classes=10, **kwargs):
        """Initialize Unet
        Args:
            min_kernel_num:num of filters in the toppest layer
        """
        super(Unet, self).__init__(**kwargs)
        self.min_kernel_num = min_kernel_num // 1  #assure that is a int
        self.kernel_num_seq = [
            self.min_kernel_num, self.min_kernel_num * 2,
            self.min_kernel_num * 4, self.min_kernel_num * 8,
            self.min_kernel_num * 16
        ]
        self.num_classes = num_classes

    def build(self, input_shape):
        self.shape = input_shape
        
        self.down_conv1 = downsamp_conv(self.kernel_num_seq[0])
        self.down_conv2 = downsamp_conv(self.kernel_num_seq[1])
        self.down_conv3 = downsamp_conv(self.kernel_num_seq[2])
        self.down_conv4 = downsamp_conv(self.kernel_num_seq[3])

        self.up_conv1 = upsamp_conv(self.kernel_num_seq[-1])
        self.up_conv2 = upsamp_conv(self.kernel_num_seq[-2])
        self.up_conv3 = upsamp_conv(self.kernel_num_seq[-3])
        self.up_conv4 = upsamp_conv(self.kernel_num_seq[-4])

        self.output_seq = keras.Sequential([
            keras.layers.Conv2D(filters=self.kernel_num_seq[0],
                                kernel_size=(3, 3),
                                padding='same'),
            keras.layers.Conv2D(filters=self.kernel_num_seq[0],
                                kernel_size=(3, 3),
                                padding='same'),
            keras.layers.Conv2D(filters=self.num_classes,
                                kernel_size=(3, 3),
                                padding='same')
        ])

        self.pooling = keras.layers.MaxPooling2D(pool_size=(2, 2))

    def call(self, inputs):
        tf.cast(inputs,dtype = tf.float32)

        conv1 = self.down_conv1(inputs)
        pool1 = self.pooling(conv1)
        conv2 = self.down_conv2(pool1)
        pool2 = self.pooling(conv2)
        conv3 = self.down_conv3(pool2)
        pool3 = self.pooling(conv3)
        conv4 = self.down_conv4(pool3)
        pool4 = self.pooling(conv4)

        up_samp1 = self.up_conv1(pool4)
        corp1 = tf.concat([conv4, up_samp1], axis=-1)
        up_samp2 = self.up_conv2(corp1)
        corp2 = tf.concat([conv3, up_samp2], axis=-1)
        up_samp3 = self.up_conv3(corp2)
        corp3 = tf.concat([conv2, up_samp3], axis=-1)
        up_samp4 = self.up_conv4(corp3)
        corp4 = tf.concat([conv1, up_samp4], axis=-1)
        output = self.output_seq(corp4)
        
        return output
