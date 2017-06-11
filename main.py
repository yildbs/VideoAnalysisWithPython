import frame_consumer
import frame_producer


if __name__ == "__main__":
    print("Start!")

    video_file_name = 'Videos/sample.avi'
    #video_file_name = 'Data/CAVIAR/OneLeaveShopReenter2cor.mpg'
    #video_file_name = 'Data/CAVIAR/EnterExitCrossingPaths2cor.mpg'

    consumer = frame_consumer.FrameConsumer()
    producer = frame_producer.FrameProducer(video_file_name, consumer)

    consumer.start()
    producer.start()

    producer.join()
    consumer.join()