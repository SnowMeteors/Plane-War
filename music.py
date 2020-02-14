import pygame

# 初始化pygame中的音乐
pygame.mixer.init()


# 播放音乐
class music(object):

    @staticmethod
    def bgm():
        return pygame.mixer.Sound("music/bgm.wav")

    @staticmethod
    def bullet():
        # 让子弹无限循环播放
        pygame.mixer.music.load("music/bullet.wav")
        pygame.mixer.music.play(-1)

    @staticmethod
    def game_over():
        return pygame.mixer.Sound("music/game_over.wav")
