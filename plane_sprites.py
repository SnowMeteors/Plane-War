import pygame
from random import randint

# 初始化pygame 貌似会加载所有其他模块的init比如font.init
pygame.init()
# pygame.font.init()
# 设置标题
pygame.display.set_caption("飞机大战")
# 设置游戏图标
pygame.display.set_icon(pygame.image.load("images/game.ico"))
# 屏幕大小的常量
SCREEN_RECT = pygame.Rect(0, 0, 480, 700)
# 刷新的帧率
FRAME_PER_SEC = 70
# 创建敌机的定时器常量
CREATE_ENEMY_EVENT = pygame.USEREVENT
# 创建敌机1s出现个数
ENEMY_CNT = randint(1, 4)
# 英雄发射子弹事件
HERO_FIRE_EVENT = pygame.USEREVENT + 1
# 奖励加成事件
BUFFER_EVENT = pygame.USEREVENT + 2
# 奖励时间到事件
BUFFER_TIME_OUT_EVENT = pygame.USEREVENT + 3
# 英雄1s发射子弹个数
HERO_FIRE_CNT = 8


# 绘制文本信息
def draw_text(content, size, color):
    pygame.font.init()
    font = pygame.font.SysFont('华文新魏', size)
    text = font.render(content, True, color)
    return text


class GameSprite(pygame.sprite.Sprite):
    """ 飞机大战 游戏精灵"""

    def __init__(self, image_name, speed=1):
        # 调用父类的初始化方法
        super().__init__()

        # 定义对象的属性
        self.image = pygame.image.load(image_name)
        self.rect = self.image.get_rect()
        self.speed = speed

    def update(self, *args):
        # 在屏幕的垂直方向上移动
        self.rect.y += self.speed


class Background(GameSprite):
    """ 游戏背景精灵 """

    def __init__(self, is_alt=False):

        # 1、调用父类方法实现精灵的创建(image/rect/speed)
        super().__init__("images/background.png")

        # 2、判断是否是交替图像，如果是，需要设置初始位置
        if is_alt:
            self.rect.y = -self.rect.height

    def update(self, *args):

        # 1、调用父类的方法实现
        super().update()

        # 2、判断是否移出屏幕，如果移出屏幕，将图像设置到屏幕的上方
        if self.rect.y >= SCREEN_RECT.height:
            self.rect.y = -self.rect.height


class Enemy(GameSprite):
    """ 敌机精灵 """

    # 敌机类型
    enemy_type = ["1", "2", "3_0"]
    # 敌机生命初始值
    life = [1, 7, 12]
    # 敌机击毁后的得分
    score = [100, 500, 1000]

    def __init__(self):

        # 是否被击中
        self.is_hit = False
        # 记录图片的下标
        self.img_index = None
        # 记录大飞机的图片数量
        self.img_count = 0
        # 敌机得分
        self.score = None
        # 敌机生命
        self.life = None
        # 概率生成 小飞机80% 中飞机15% 大飞机5%
        self.probability = [80, 95, 100]
        # 敌机速度不同种类速度不一样 小飞机的速度随机生成
        speed = [randint(2, 8), 3, 1]
        # 随机数生成
        Probability = randint(1, 100)
        for i in range(3):
            if Probability <= self.probability[i]:
                # 1、调用父类方法，创建敌机精灵，同时指定敌机图片
                super().__init__("images/enemy" + str(Enemy.enemy_type[i]) + ".png")
                # 2、指定敌机的初始随机速度
                self.speed = speed[i]
                # 3、指定敌机的初始随机位置
                self.rect.x = randint(0, SCREEN_RECT.width - self.rect.width)
                self.rect.y = -self.rect.height  # 从屏幕开始飞出
                # 4、指定敌机生命
                self.life = Enemy.life[i]
                # 5、指定敌机得分
                self.score = Enemy.score[i]
                # 6、更新图片下标
                self.img_index = i + 1
                break

    def update(self, *args):
        # 1、调用父类方法：保持垂直方向的飞行
        super().update()

        # 2、判断是否飞出屏幕，如果是，需要从精灵组删除敌机
        if self.rect.y >= SCREEN_RECT.height:
            # kill方法可以将精灵从所有精灵组中移出，精灵内存自动销毁
            self.kill()

        # 3、加载击中图片
        self.isHit()

    # 加载被击中图片
    def isHit(self):
        # 小飞机没有被击中的图片
        if self.img_index != 1:
            # 如果被击中
            if self.is_hit:
                # 当前图片就等于被击中的图片
                self.image = pygame.image.load("images/enemy" + str(self.img_index) + "_hit.png")
                # 重置标志
                self.is_hit = False
            else:
                # 大飞机动图加载
                if self.img_index == 3:
                    self.image = pygame.image.load("images/enemy3_" + str(self.img_count % 2) + ".png")
                    self.img_count += 1
                # 加载中飞机
                else:
                    self.image = pygame.image.load("images/enemy2.png")


class Hero(GameSprite):
    """ 英雄精灵 """
    # 英雄图片的下标
    images_index = 0

    def __init__(self):
        # 调用父类方法，设置image&speed
        super().__init__("images/me0.png", 0)

        # 设置英雄的初始位置
        self.rect.centerx = SCREEN_RECT.centerx
        self.rect.y = SCREEN_RECT.height - self.rect.height - 50

        # 创建子弹精灵组
        self.bullets = pygame.sprite.Group()

        # 初始英雄有3条生命
        self.life = 3

        # 英雄是否无敌
        self.isInvincible = False

        # 英雄是否得到加成
        self.isBuffer = False

    # 英雄移动
    def update(self, *args):
        # 要么键盘移动要么鼠标移动不能共存
        # self.keyboardMove()
        self.mouseMove()
        self.jetAnimation()

    # 键盘移动
    def keyboardMove(self):

        # 使用键盘提供的方法获取键盘按键 - 按键元组
        keys_pressed = pygame.key.get_pressed()
        # 判断元组中对应的按键索引值 是否按了光标键 或者wasd
        if keys_pressed[pygame.K_UP] or keys_pressed[pygame.K_DOWN] or keys_pressed[pygame.K_RIGHT] or \
                keys_pressed[pygame.K_LEFT] or keys_pressed[pygame.K_w] or keys_pressed[pygame.K_s] or \
                keys_pressed[pygame.K_d] or keys_pressed[pygame.K_a]:

            # 改变速度
            self.speed = 4

            # 按了上键
            if (keys_pressed[pygame.K_UP] or keys_pressed[pygame.K_w]) and self.rect.top > 0:
                self.rect.y -= self.speed
            # 按了下键
            elif (keys_pressed[pygame.K_DOWN] or keys_pressed[pygame.K_s]) and self.rect.bottom < SCREEN_RECT.height:
                self.rect.y += self.speed
            # 按了左键
            elif (keys_pressed[pygame.K_LEFT] or keys_pressed[pygame.K_a]) and self.rect.left > 0:
                self.rect.x -= self.speed
            # 按了右键
            elif (keys_pressed[pygame.K_RIGHT] or keys_pressed[pygame.K_d]) and self.rect.right < SCREEN_RECT.width:
                self.rect.x += self.speed
        else:
            self.speed = 0  # 将速度还原

    # 光标移动
    def mouseMove(self):
        # 获取我方飞机的绝对位置
        # 坐标是从0,0开始算
        pos_x, pos_y = pygame.mouse.get_pos()
        # 设置坐标在飞机中心
        pos_x -= self.rect.width / 2
        pos_y -= self.rect.height / 2
        # 飞机坐标等于鼠标坐标
        self.rect.y = pos_y
        self.rect.x = pos_x

    # 发射子弹
    def fire(self):

        # 英雄得到加成一次性加载2发子弹
        for i in range(2):
            # 创建子弹精灵
            bullet = Bullet(self.isBuffer)
            # 利用三目运算符设置子弹的位置
            bullet.rect.x = self.rect.centerx - 1 if (not self.isBuffer) else ((self.rect.centerx - 35) + 65 * i)
            bullet.rect.y = self.rect.top - 5 if (not self.isBuffer) else self.rect.top + 30
            # 将子弹精灵添加进精灵组
            self.bullets.add(bullet)
            # 没有得到加成就循环一次
            if not self.isBuffer:
                break

    # 喷气动画
    def jetAnimation(self):
        # 动画效果不是太完美，闪的太快了
        # 加载图片轮流播放要么是0 要么是1
        self.image = pygame.image.load("images/me" + str(Hero.images_index % 2) + ".png")
        Hero.images_index += 1


class Bullet(GameSprite):
    """ 子弹精灵 """

    # 特殊子弹
    def __init__(self, isBuffer=False):
        # 调用父类方法，设置子弹图片，设置初始速度

        # python的三目运算符真反人类
        super().__init__("images/bullet1.png" if (not isBuffer) else "images/bullet2.png", -12)

    def update(self, *args):
        # 调用父类方法，让子弹沿着垂直方向飞行
        super().update()

        # 判断子弹是否飞出屏幕
        if self.rect.bottom < 0:
            self.kill()


class HeroLifeImg(GameSprite):
    """英雄生命图片精灵"""

    # life=英雄生命值
    def __init__(self, life):
        # 调用父类方法
        super().__init__("images/life.png", 0)
        # 重新设置x，y值
        self.rect.y = SCREEN_RECT.height - self.rect.height
        self.rect.x = SCREEN_RECT.width - self.rect.width * life


class Buffer(GameSprite):
    """ 子弹加成精灵 """

    def __init__(self):
        # 调用父类方法
        super().__init__("images/bullet_supply.png")
        # 重新设置位置
        self.rect.x = randint(0, SCREEN_RECT.width - self.rect.width)
        self.rect.y = -self.rect.height

    def update(self, *args):
        # 调用父类更新
        super().update()

        # 判断是否飞出屏幕
        if self.rect.y >= SCREEN_RECT.height:
            # 移除精灵
            self.kill()
