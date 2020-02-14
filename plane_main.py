# coding    : utf-8
# @Time     : 2020/2/9
# @EndTime  : 2020/2/13
# @Author   : 麦当
# @Software : 飞机大战
# @Filename : plane_main

# 爆炸效果如果实现的话，再爆炸的时候其他精灵要等爆炸图循环完毕才能动，还不如不实现爆炸效果

from plane_sprites import *
from time import sleep
from music import *
import os


class PlaneGame(object):
    """ 飞机大战主游戏 """

    # 历史最高分
    TopScore = 0
    # 是否显示首页
    isShowHome = True

    # 数据初始
    def __init__(self):

        # 1、创建游戏的窗口
        self.screen = pygame.display.set_mode(SCREEN_RECT.size)
        if PlaneGame.isShowHome:
            self.__game_home()
            PlaneGame.isShowHome = False
        # 2、创建游戏的时钟
        self.clock = pygame.time.Clock()
        # 3、调用私有方法,精灵和精灵组的创建
        self.__create_sprites()
        # 4、设置定时器事件  第二个参数是多少毫秒出现必须是int类型
        # 创建敌机
        pygame.time.set_timer(CREATE_ENEMY_EVENT, int(1000 / ENEMY_CNT))
        # 创建子弹
        pygame.time.set_timer(HERO_FIRE_EVENT, int(1000 / HERO_FIRE_CNT))
        # 创建子弹加成
        pygame.time.set_timer(BUFFER_EVENT, randint(10, 35) * 1000)
        # 5、设置当前游戏分数
        self.score = 0
        # 6、获取历史最高分
        self.__get_score()
        # 7、加载音乐
        self.__load_music()

    # 游戏首页
    def __game_home(self):
        self.screen.blit(pygame.image.load("images/home.png"), (0, 0))
        startGameImg = pygame.image.load("images/start_game.png")
        startGameImgRect = startGameImg.get_rect()
        startGameImgRect.centerx = SCREEN_RECT.centerx
        startGameImgRect.y = SCREEN_RECT.bottom - startGameImgRect.height - 165
        self.screen.blit(startGameImg, startGameImgRect)
        pygame.display.update()
        self.__mouse_click(startGameImgRect, 1)

    # 创建精灵
    def __create_sprites(self):

        # 创建背景精灵和精灵组
        bg1 = Background()
        bg2 = Background(True)
        self.back_group = pygame.sprite.Group(bg1, bg2)

        # 创建敌机精灵组
        self.enemy_group = pygame.sprite.Group()

        # 创建英雄的精灵和精灵组
        self.hero = Hero()
        self.hero_group = pygame.sprite.Group(self.hero)

        # 创建英雄生命精灵组
        self.hero_life_group = pygame.sprite.Group()
        for i in range(self.hero.life):
            # 依次向组中添加精灵
            self.hero_life_group.add(HeroLifeImg(i + 1))

        # 创建子弹加成精灵组
        self.buffer_group = pygame.sprite.Group()

    # 开始游戏
    def start_game(self):

        while self.hero.life > 0:
            # 1、设置刷新帧
            self.clock.tick(FRAME_PER_SEC)
            # 2、事件监听
            self.__event_handler()
            # 3、更新/绘制精灵组
            self.__update_sprites()
            # 4、绘制字体
            self.__draw_font()
            # 5、碰撞检测
            self.__check_collide()
            # 6、更新显示
            pygame.display.update()

    # 事件监听
    def __event_handler(self):
        for event in pygame.event.get():
            # 判断是否退出游戏
            if event.type == pygame.QUIT:
                self.__close_game()

            # 判断加成时间是否到
            elif event.type == BUFFER_TIME_OUT_EVENT:
                self.hero.isBuffer = False

            # 判断是否生成敌机
            elif event.type == CREATE_ENEMY_EVENT:
                # 创建敌机精灵
                enemy = Enemy()
                # 将敌机精灵添加到敌机精灵组
                self.enemy_group.add(enemy)

            # 判断是否生成子弹加成
            elif event.type == BUFFER_EVENT:
                # 添加进子弹加成精灵组
                self.buffer_group.add(Buffer())
                # 重新设置子弹加成定时器
                pygame.time.set_timer(BUFFER_EVENT, randint(10, 35) * 1000)

            # 判断是否发射子弹
            elif event.type == HERO_FIRE_EVENT:
                self.hero.fire()

            # 判断是否按了空格键
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                # 是否无敌
                if self.hero.isInvincible:
                    self.hero.isInvincible = False
                else:
                    self.hero.isInvincible = True

            # 判断用户是否按了鼠标键
            # 1是左键 2是中键 3是右键
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                # 暂停子弹射击音效
                pygame.mixer.music.pause()
                # 提示继续游戏信息
                self.screen.blit(draw_text("请将鼠标放到飞机上再恢复游戏", 26, (255, 0, 0)), (56, 55))
                pygame.display.update()  # 更新显示
                # 鼠标点击函数
                self.__mouse_click(self.hero.rect, 3)
                # 恢复子弹射击音效
                pygame.mixer.music.unpause()

            # 这种写法一直按一个键等于按一次
            # elif event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
            #     print("右移")

    # 碰撞检测
    def __check_collide(self):
        # 子弹摧毁敌机
        # 精灵组碰撞检测函数 第一个参数和第二个参数传入精灵组 第三个参数和第四个参数传入是否销毁该精灵
        # pygame.sprite.groupcollide(self.hero.bullets, self.enemy_group, True, True)
        # 精确到像素点
        for enemy in self.enemy_group:
            for bullet in self.hero.bullets:
                # 发生了碰撞
                if pygame.sprite.collide_mask(bullet, enemy):
                    enemy.is_hit = True
                    # 立即移除子弹精灵
                    self.hero.bullets.remove(bullet)
                    # 判断敌机生命值
                    if enemy.life - 1 > 0:
                        enemy.life -= 1
                    else:
                        self.score += enemy.score  # 小飞机击毁,增加分数
                        # 从精灵组中删除效果等于enemy.kill()
                        self.enemy_group.remove(enemy)
                        break

        # 第一版 这个版本是两个图形直接碰撞
        """
        # 飞机碰撞敌机
        enemies = pygame.sprite.spritecollide(self.hero, self.enemy_group, True, False)

        # 判断列表是否有内容
        if len(enemies) > 0:
            # 游戏结束
            self.__game_over()
        """

        # 第二版 两个可见范围内发生碰撞
        # 遍历敌机精灵组中的每个精灵是否与英雄精灵发生碰撞
        # 当英雄不是无敌的时候,开启碰撞检测功能
        if not self.hero.isInvincible:
            for enemy in self.enemy_group:
                # 发生了碰撞
                if pygame.sprite.collide_mask(self.hero, enemy):

                    # 判断英雄是否死亡
                    if self.hero.life > 0:
                        # 直接让敌机死亡
                        enemy.kill()
                        # 英雄减命
                        self.hero.life -= 1
                        # 计时器设置
                        # 不知道怎么直接删除精灵组中最后一个精灵
                        cnt = 0
                        for hero_life in self.hero_life_group:
                            # 只有根据英雄的生命值来判断
                            if cnt == self.hero.life:
                                # 移除最后一个精灵
                                self.hero_life_group.remove(hero_life)
                            cnt += 1

                    # 这里不写else的原因是要同时更新最后一张生命图片
                    if self.hero.life <= 0:
                        # 暂停播放所有音效
                        self.bgm.stop()
                        pygame.mixer.music.stop()
                        # 播放游戏结束音乐
                        self.game_over_music.play()

                        # 播放飞机爆炸图片
                        self.__Plane_explosion()
                        self.__game_over()
                        return  # 进入游戏结束后 直接退出此函数

        # 英雄是否吃到了子弹加成
        for buffer in self.buffer_group:
            if pygame.sprite.collide_mask(buffer, self.hero):
                # 移除子弹加成精灵
                self.buffer_group.remove(buffer)
                self.hero.isBuffer = True
                # 创建子弹加成定时器 15s加成时间
                pygame.time.set_timer(BUFFER_TIME_OUT_EVENT, 15 * 1000)

    # 更新精灵
    def __update_sprites(self):

        # 更新背景
        self.back_group.draw(self.screen)
        self.back_group.update()

        # 更新敌机
        self.enemy_group.draw(self.screen)
        self.enemy_group.update()

        # 更新我方飞机
        self.hero_group.draw(self.screen)
        self.hero_group.update()

        # 更新子弹
        self.hero.bullets.draw(self.screen)
        self.hero.bullets.update()

        # 绘制英雄生命图片
        self.hero_life_group.draw(self.screen)

        # 测试
        self.buffer_group.draw(self.screen)
        self.buffer_group.update()

    # 飞机爆炸
    def __Plane_explosion(self):

        for i in range(1, 5):
            # 显示背景图片
            self.back_group.draw(self.screen)
            # 显示敌机
            self.enemy_group.draw(self.screen)
            # 显示爆炸效果
            self.screen.blit(pygame.image.load("images/me_destroy_" + str(i) + ".png"), self.hero.rect)
            # 更新显示
            pygame.display.update()
            sleep(0.12)  # 让爆炸效果慢一点
        sleep(0.12)  # 再次延时

    # 绘制字体
    def __draw_font(self):
        # 显示分数
        self.screen.blit(draw_text(str(self.score), 40, (255, 255, 255)), (60, 5))
        # 显示暂停按钮
        self.screen.blit(pygame.image.load("images/pause_nor.png"), (0, 0))
        # 英雄无敌
        if self.hero.isInvincible:
            self.screen.blit(draw_text("已开启无敌模式", 26, (0, 0, 0)), (0, SCREEN_RECT.bottom - 25))

    # 游戏结束
    def __game_over(self):

        # 释放英雄内存
        self.hero.kill()
        # 绘制game_over后的图片
        self.__draw_game_over_img()
        # 更新分数
        self.__update_score()
        # 绘制分数
        self.__draw_game_over_score()
        # 更新显示
        pygame.display.update()
        # 重新开始游戏
        self.__restart_game()

    # 更新分数
    def __update_score(self):

        # 文件不存在 或者文件为空
        if not os.path.exists("score.txt") or os.path.getsize("score.txt") == 0:
            # 以写入的方式打开，如果该文件不存在则创建
            file = open("score.txt", "w")
            # 写入当前分数
            file.write(str(self.score))
            PlaneGame.TopScore = self.score
            # 关闭文件
            file.close()

        else:
            # 默认以只读的方式打开
            file = open("score.txt")
            # 获取最高分
            PlaneGame.TopScore = int(file.read())
            # 关闭文件
            file.close()
            # 当前分数大于最高分
            if self.score > PlaneGame.TopScore:
                PlaneGame.TopScore = self.score  # 更新最高分
                file = open("score.txt", "w")
                file.write(str(PlaneGame.TopScore))
                file.close()

    # 结束分数
    def __draw_game_over_score(self):

        # 设置当前分数各属性
        CurrentScoreFont = draw_text(str(self.score), 40, (255, 255, 255))
        CurrentScoreRect = CurrentScoreFont.get_rect()
        CurrentScoreRect.x = SCREEN_RECT.width / 2 - CurrentScoreRect.width / 2
        CurrentScoreRect.y = SCREEN_RECT.height - 252
        self.screen.blit(CurrentScoreFont, CurrentScoreRect)

        # 设置最高分数各属性
        TopScoreFont = draw_text(str(PlaneGame.TopScore), 40, (255, 255, 255))
        TopScoreRect = TopScoreFont.get_rect()
        TopScoreRect.x = SCREEN_RECT.width / 2 - TopScoreRect.width / 2
        TopScoreRect.y = 215
        self.screen.blit(TopScoreFont, TopScoreRect)

    # 结束图片
    def __draw_game_over_img(self):
        # 绘制结束图片
        self.screen.blit(pygame.image.load("images/game_over.png"), (0, 0))
        # 设置重新开始图片各属性
        again_img = pygame.image.load("images/again.png")
        self.again_img_rect = again_img.get_rect()
        self.again_img_rect.centerx = SCREEN_RECT.centerx
        self.again_img_rect.y = SCREEN_RECT.bottom - self.again_img_rect.height - 80
        # 绘制重新开始图片
        self.screen.blit(again_img, self.again_img_rect)

    # 重新开始
    def __restart_game(self):

        # 鼠标点击事件
        self.__mouse_click(self.again_img_rect, 1)

        # 清空所有精灵
        self.back_group.empty()
        self.enemy_group.empty()
        self.buffer_group.empty()
        self.hero_group.empty()
        self.hero_life_group.empty()

        # 删除所有精灵组
        del self.back_group
        del self.enemy_group
        del self.buffer_group
        del self.hero_group
        del self.hero_life_group

    # 鼠标点击
    def __mouse_click(self, objects, key):

        # 对象值 和 鼠标点击值 1 左键 2 中键 3 右键
        isClick = False
        while not isClick:
            # 获取光标绝对位置
            x, y = pygame.mouse.get_pos()
            # 获取事件列表
            for event in pygame.event.get():
                # 图像被点击
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == key and \
                        objects.left <= x <= objects.right and objects.top <= y <= objects.bottom:
                    # 退出循环
                    isClick = True
                    break
                # 判断是否退出程序
                elif event.type == pygame.QUIT:
                    self.__close_game()

    # 加载音乐
    def __load_music(self):
        # 获取bgm
        self.bgm = music().bgm()
        # 循环1000次，这玩意没有无限循环
        self.bgm.play(1000)
        # 无限播放子弹射击音效
        music().bullet()
        # 获取game_over音效
        self.game_over_music = music().game_over()

    # 关闭游戏
    @staticmethod
    def __close_game():
        # 退出pygame
        pygame.quit()
        # 退出整个程序
        exit()

    # 获取分数
    @staticmethod
    def __get_score():
        # 文件存在并且有数据
        if os.path.exists("score.txt") and os.path.getsize("score.txt"):
            file = open("score.txt")
            PlaneGame.TopScore = int(file.read())
            file.close()


if __name__ == '__main__':

    while True:
        PlaneGame().start_game()
