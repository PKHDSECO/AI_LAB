import pygame
import numpy as np
import random
import math
import sys
import os

# Pygame 초기화
pygame.init()
pygame.mixer.init()  # 사운드 초기화

# 화면 설정
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('3D 오목 게임 - Light Version')

# 색상 정의
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
BROWN = (139, 69, 19)
LIGHT_BROWN = (205, 133, 63)
DARK_BROWN = (101, 67, 33)
STONE_BLACK = (20, 20, 20)
STONE_WHITE = (220, 220, 220)
BOARD_COLOR = (222, 184, 135)

# 게임 설정
BOARD_SIZE = 15
CELL_SIZE = 35
BOARD_OFFSET_X = 100
BOARD_OFFSET_Y = 100

class Particle:
    """폭죽 파티클 클래스"""
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-5, 5)
        self.vy = random.uniform(-8, -2)
        self.color = color
        self.life = 60
        self.max_life = 60
        self.size = random.randint(2, 6)
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.3  # 중력
        self.life -= 1
        self.size = max(0, self.size - 0.1)
    
    def draw(self, screen):
        if self.life > 0:
            alpha = int(255 * (self.life / self.max_life))
            color = (*self.color, alpha)
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.size))

class Gomoku3DLight:
    def __init__(self):
        self.board = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int)
        self.current_player = 1  # 1: 흑, 2: 백
        self.game_over = False
        self.winner = None
        self.last_move = None
        self.ai_mode = True
        self.ai_player = 2  # AI는 백돌
        self.ai_difficulty = "중"  # 난이도: 하, 중, 상
        self.ai_delay = 2000  # AI 지연 시간 (밀리초)
        self.last_ai_time = 0
        
        # 폭죽 효과
        self.particles = []
        self.show_celebration = False
        self.celebration_timer = 0
        
        # 3D 효과를 위한 설정
        self.camera_angle = 0
        self.camera_distance = 200
        self.camera_height = 50
        
        # 폰트 설정 (한글 지원)
        try:
            # Windows 기본 한글 폰트
            self.font = pygame.font.Font("C:/Windows/Fonts/malgun.ttf", 36)
            self.small_font = pygame.font.Font("C:/Windows/Fonts/malgun.ttf", 24)
            self.title_font = pygame.font.Font("C:/Windows/Fonts/malgun.ttf", 48)
        except:
            try:
                # 대체 한글 폰트
                self.font = pygame.font.Font("C:/Windows/Fonts/gulim.ttc", 36)
                self.small_font = pygame.font.Font("C:/Windows/Fonts/gulim.ttc", 24)
                self.title_font = pygame.font.Font("C:/Windows/Fonts/gulim.ttc", 48)
            except:
                # 기본 폰트 사용
                self.font = pygame.font.Font(None, 36)
                self.small_font = pygame.font.Font(None, 24)
                self.title_font = pygame.font.Font(None, 48)
        
        # 게임 상태
        self.show_menu = True
        self.game_mode = "AI"  # "AI" or "2P"
        self.menu_selection = 0
        self.difficulty_selection = 1  # 0: 하, 1: 중, 2: 상
        
        # 게임 종료 후 선택 상태
        self.show_game_over_menu = False
        self.game_over_selection = 0  # 0: 다시 하기, 1: 나가기
        
        # 돌 선택 기능
        self.stone_selection = 1  # 0: 기본, 1: BC_CARD_CI, 2: 사용자 선택
        self.custom_stone_path = "gomoku_re/BC_CARD_CI.svg"  # 기본 경로 설정
        self.available_stones = [
            "기본 돌",
            "BC_CARD_CI 스타일",
            "사용자 이미지",
            "얼굴 이미지"
        ]
        
        # 사운드 로드
        self.load_sounds()
        
        # 이미지 로드
        self.load_images()
    
    def load_sounds(self):
        """사운드 파일 로드"""
        try:
            # 간단한 사운드 생성 (실제 파일이 없을 경우)
            self.stone_sound = self.create_stone_sound()
            self.win_sound = self.create_win_sound()
            print("사운드 로드 성공")
        except Exception as e:
            print(f"사운드 로드 실패: {e}")
            self.stone_sound = None
            self.win_sound = None
    
    def load_images(self):
        """이미지 파일 로드"""
        try:
            # 기본 이미지들 생성
            self.default_black_stone = self.create_stone_image(STONE_BLACK)
            self.bc_card_black_stone = self.create_special_black_stone()
            self.white_stone_image = self.create_stone_image(STONE_WHITE)
            
            # 현재 선택된 돌 이미지 설정
            self.update_stone_images()
            
            print("이미지 로드 성공")
            
        except Exception as e:
            print(f"이미지 로드 실패: {e}")
            self.default_black_stone = None
            self.bc_card_black_stone = None
            self.white_stone_image = None
            self.black_stone_image = None
    
    def update_stone_images(self):
        """선택된 돌에 따라 이미지 업데이트"""
        print(f"돌 선택 업데이트: {self.stone_selection} - {self.available_stones[self.stone_selection]}")
        
        if self.stone_selection == 0:  # 기본 돌
            self.black_stone_image = self.default_black_stone
            print("기본 돌로 설정됨")
        elif self.stone_selection == 1:  # BC_CARD_CI 스타일
            self.black_stone_image = self.bc_card_black_stone
            print("BC_CARD_CI 스타일로 설정됨")
        elif self.stone_selection == 2:  # 사용자 이미지
            if self.custom_stone_path and os.path.exists(self.custom_stone_path):
                try:
                    # 사용자 이미지 로드 및 크기 조정
                    user_image = pygame.image.load(self.custom_stone_path)
                    size = CELL_SIZE - 6
                    self.black_stone_image = pygame.transform.scale(user_image, (size, size))
                    print(f"사용자 이미지 로드 성공: {self.custom_stone_path}")
                except Exception as e:
                    print(f"사용자 이미지 로드 실패: {e}, BC_CARD_CI 스타일 사용")
                    self.black_stone_image = self.bc_card_black_stone
            else:
                print("사용자 이미지 경로가 없거나 파일이 존재하지 않음, BC_CARD_CI 스타일 사용")
                self.black_stone_image = self.bc_card_black_stone
        elif self.stone_selection == 3:  # 얼굴 이미지
            face_path = "gomoku_re/IMG_7541.jpeg"
            if os.path.exists(face_path):
                try:
                    # 얼굴 이미지 로드 및 배경 제거
                    self.black_stone_image = self.create_face_stone(face_path)
                    print(f"얼굴 이미지 로드 성공: {face_path}")
                except Exception as e:
                    print(f"얼굴 이미지 로드 실패: {e}, BC_CARD_CI 스타일 사용")
                    self.black_stone_image = self.bc_card_black_stone
            else:
                print("얼굴 이미지 파일이 존재하지 않음, BC_CARD_CI 스타일 사용")
                self.black_stone_image = self.bc_card_black_stone
    
    def create_special_black_stone(self):
        """BC_CARD_CI.svg를 기반으로 한 특별한 흑돌 이미지 생성"""
        size = CELL_SIZE - 6
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        center = size // 2
        radius = size // 2 - 2
        
        # 그림자
        pygame.draw.circle(surface, DARK_BROWN, (center + 2, center + 2), radius)
        
        # 메인 돌 (어두운 회색)
        pygame.draw.circle(surface, (40, 40, 40), (center, center), radius)
        
        # BC_CARD_CI 스타일의 하이라이트 (카드 느낌)
        highlight_radius = radius // 2
        pygame.draw.circle(surface, (80, 80, 80), 
                         (center - highlight_radius//2, center - highlight_radius//2), 
                         highlight_radius)
        
        # 추가 하이라이트
        small_highlight = radius // 4
        pygame.draw.circle(surface, (120, 120, 120), 
                         (center - small_highlight, center - small_highlight), 
                         small_highlight)
        
        # 테두리 (카드 느낌)
        pygame.draw.circle(surface, (20, 20, 20), (center, center), radius, 1)
        
        return surface
    
    def create_face_stone(self, face_path):
        """얼굴 이미지를 돌로 변환 (흰색 배경 제거, 고해상도)"""
        try:
            # 원본 이미지 로드
            original_image = pygame.image.load(face_path)
            
            # 고해상도로 처리하기 위해 더 큰 크기로 먼저 스케일링
            high_res_size = CELL_SIZE * 2  # 2배 크기로 처리
            high_res_image = pygame.transform.scale(original_image, (high_res_size, high_res_size))
            
            # 최종 돌 크기 (더 크게)
            final_size = CELL_SIZE - 2  # 기존보다 4픽셀 더 크게
            
            # 투명 배경의 새 서피스 생성
            surface = pygame.Surface((high_res_size, high_res_size), pygame.SRCALPHA)
            
            # 고해상도 이미지 데이터 가져오기
            image_array = pygame.surfarray.array3d(high_res_image)
            
            # 흰색 배경 제거 (임계값 기반) - 고해상도에서 처리
            for x in range(high_res_size):
                for y in range(high_res_size):
                    pixel = image_array[x][y]
                    # 흰색에 가까운 픽셀을 투명하게 만들기
                    if (pixel[0] > 200 and pixel[1] > 200 and pixel[2] > 200):
                        # 투명하게 설정
                        surface.set_at((x, y), (0, 0, 0, 0))
                    else:
                        # 원본 픽셀 유지
                        surface.set_at((x, y), (*pixel, 255))
            
            # 원형 마스크 적용 (돌 모양으로) - 고해상도에서 처리
            center = high_res_size // 2
            radius = high_res_size // 2 - 4
            
            # 원형 마스크 생성
            mask_surface = pygame.Surface((high_res_size, high_res_size), pygame.SRCALPHA)
            pygame.draw.circle(mask_surface, (255, 255, 255, 255), (center, center), radius)
            
            # 마스크 적용
            masked_surface = pygame.Surface((high_res_size, high_res_size), pygame.SRCALPHA)
            masked_surface.blit(surface, (0, 0))
            masked_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            
            # 최종 크기로 스케일링 (고해상도에서 처리한 후)
            final_surface = pygame.transform.scale(masked_surface, (final_size, final_size))
            
            # 그림자 효과 추가 (최종 크기에서)
            shadow_surface = pygame.Surface((final_size, final_size), pygame.SRCALPHA)
            shadow_center = final_size // 2
            shadow_radius = final_size // 2 - 2
            pygame.draw.circle(shadow_surface, (*DARK_BROWN, 128), (shadow_center + 2, shadow_center + 2), shadow_radius)
            
            # 최종 이미지에 그림자 합성
            final_surface.blit(shadow_surface, (0, 0))
            
            print(f"얼굴 이미지 처리 완료: {high_res_size}x{high_res_size} -> {final_size}x{final_size}")
            return final_surface
            
        except Exception as e:
            print(f"얼굴 이미지 처리 실패: {e}")
            # 실패 시 기본 돌 반환
            return self.create_stone_image(STONE_BLACK)
    
    def create_stone_image(self, color):
        """돌 이미지 생성"""
        size = CELL_SIZE - 6  # 돌 크기
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # 원형 돌 그리기
        center = size // 2
        radius = size // 2 - 2
        
        # 그림자
        pygame.draw.circle(surface, DARK_BROWN, (center + 2, center + 2), radius)
        
        # 메인 돌
        pygame.draw.circle(surface, color, (center, center), radius)
        
        # 하이라이트
        highlight_radius = radius // 3
        if color == STONE_BLACK:
            highlight_color = (50, 50, 50)
        else:
            highlight_color = (255, 255, 255)
        
        pygame.draw.circle(surface, highlight_color, 
                         (center - highlight_radius, center - highlight_radius), 
                         highlight_radius)
        
        # 백돌인 경우 테두리
        if color == STONE_WHITE:
            pygame.draw.circle(surface, BLACK, (center, center), radius, 2)
        
        return surface
    
    def create_stone_sound(self):
        """돌 놓는 소리 생성"""
        try:
            sample_rate = 44100
            duration = 0.1
            samples = int(sample_rate * duration)
            
            # 간단한 딱 소리 생성 (모노)
            sound_array = np.zeros(samples, dtype=np.int16)
            for i in range(samples):
                t = i / sample_rate
                if t < duration:
                    # 감쇠하는 사인파
                    frequency = 800 * math.exp(-t * 10)
                    sound_array[i] = int(32767 * 0.3 * math.sin(2 * math.pi * frequency * t) * math.exp(-t * 20))
            
            # Pygame 사운드 객체 생성
            sound = pygame.sndarray.make_sound(sound_array)
            return sound
        except Exception as e:
            print(f"돌 소리 생성 실패: {e}")
            return None
    
    def create_win_sound(self):
        """승리 소리 생성"""
        try:
            sample_rate = 44100
            duration = 0.5
            samples = int(sample_rate * duration)
            
            # 승리 팡파르 생성 (모노)
            sound_array = np.zeros(samples, dtype=np.int16)
            for i in range(samples):
                t = i / sample_rate
                if t < duration:
                    # 상승하는 음계
                    frequency = 440 + 200 * t
                    sound_array[i] = int(32767 * 0.2 * math.sin(2 * math.pi * frequency * t) * math.exp(-t * 2))
            
            sound = pygame.sndarray.make_sound(sound_array)
            return sound
        except Exception as e:
            print(f"승리 소리 생성 실패: {e}")
            return None
    
    def create_celebration(self, x, y):
        """폭죽 효과 생성"""
        colors = [RED, GREEN, BLUE, YELLOW, WHITE]
        for _ in range(50):
            color = random.choice(colors)
            self.particles.append(Particle(x, y, color))
    
    def update_particles(self):
        """파티클 업데이트"""
        for particle in self.particles[:]:
            particle.update()
            if particle.life <= 0:
                self.particles.remove(particle)
    
    def draw_particles(self):
        """파티클 그리기"""
        for particle in self.particles:
            particle.draw(screen)
    
    def draw_3d_board(self):
        """3D 효과가 적용된 오목판 그리기"""
        # 보드 배경 (그림자 효과)
        shadow_offset = 5
        pygame.draw.rect(screen, DARK_BROWN, 
                        (BOARD_OFFSET_X + shadow_offset, BOARD_OFFSET_Y + shadow_offset, 
                         BOARD_SIZE * CELL_SIZE, BOARD_SIZE * CELL_SIZE))
        
        # 보드 배경
        pygame.draw.rect(screen, BOARD_COLOR, 
                        (BOARD_OFFSET_X, BOARD_OFFSET_Y, 
                         BOARD_SIZE * CELL_SIZE, BOARD_SIZE * CELL_SIZE))
        
        # 3D 효과를 위한 테두리
        pygame.draw.rect(screen, DARK_BROWN, 
                        (BOARD_OFFSET_X, BOARD_OFFSET_Y, 
                         BOARD_SIZE * CELL_SIZE, BOARD_SIZE * CELL_SIZE), 3)
        
        # 격자 그리기 (3D 효과)
        for i in range(BOARD_SIZE):
            # 세로선
            x = BOARD_OFFSET_X + i * CELL_SIZE
            # 그림자
            pygame.draw.line(screen, DARK_BROWN, 
                           (x + 2, BOARD_OFFSET_Y + 2), 
                           (x + 2, BOARD_OFFSET_Y + BOARD_SIZE * CELL_SIZE - 2), 1)
            # 실제 선
            pygame.draw.line(screen, BLACK, 
                           (x, BOARD_OFFSET_Y), 
                           (x, BOARD_OFFSET_Y + BOARD_SIZE * CELL_SIZE), 2)
            
            # 가로선
            y = BOARD_OFFSET_Y + i * CELL_SIZE
            # 그림자
            pygame.draw.line(screen, DARK_BROWN, 
                           (BOARD_OFFSET_X + 2, y + 2), 
                           (BOARD_OFFSET_X + BOARD_SIZE * CELL_SIZE - 2, y + 2), 1)
            # 실제 선
            pygame.draw.line(screen, BLACK, 
                           (BOARD_OFFSET_X, y), 
                           (BOARD_OFFSET_X + BOARD_SIZE * CELL_SIZE, y), 2)
        
        # 별점 그리기 (3D 효과)
        star_points = [3, 7, 11]
        for x in star_points:
            for y in star_points:
                center_x = BOARD_OFFSET_X + x * CELL_SIZE
                center_y = BOARD_OFFSET_Y + y * CELL_SIZE
                
                # 그림자
                pygame.draw.circle(screen, DARK_BROWN, (center_x + 2, center_y + 2), 3)
                # 실제 별점
                pygame.draw.circle(screen, BLACK, (center_x, center_y), 3)
    
    def draw_3d_stone(self, x, y, player):
        """3D 효과가 적용된 돌 그리기 (이미지 사용)"""
        center_x = BOARD_OFFSET_X + x * CELL_SIZE
        center_y = BOARD_OFFSET_Y + y * CELL_SIZE
        
        if player == 1:  # 흑돌
            if self.black_stone_image:
                # 이미지 사용
                image_rect = self.black_stone_image.get_rect(center=(center_x, center_y))
                screen.blit(self.black_stone_image, image_rect)
            else:
                # 기본 원형 그리기
                radius = CELL_SIZE // 2 - 3
                pygame.draw.circle(screen, DARK_BROWN, (center_x + 3, center_y + 3), radius)
                pygame.draw.circle(screen, STONE_BLACK, (center_x, center_y), radius)
                pygame.draw.circle(screen, (50, 50, 50), (center_x - radius//3, center_y - radius//3), radius//3)
        else:  # 백돌
            if self.white_stone_image:
                # 이미지 사용
                image_rect = self.white_stone_image.get_rect(center=(center_x, center_y))
                screen.blit(self.white_stone_image, image_rect)
            else:
                # 기본 원형 그리기
                radius = CELL_SIZE // 2 - 3
                pygame.draw.circle(screen, DARK_BROWN, (center_x + 3, center_y + 3), radius)
                pygame.draw.circle(screen, STONE_WHITE, (center_x, center_y), radius)
                pygame.draw.circle(screen, (255, 255, 255), (center_x - radius//3, center_y - radius//3), radius//3)
                pygame.draw.circle(screen, BLACK, (center_x, center_y), radius, 2)
    
    def draw_stones(self):
        """모든 돌 그리기"""
        for x in range(BOARD_SIZE):
            for y in range(BOARD_SIZE):
                if self.board[x][y] != 0:
                    self.draw_3d_stone(x, y, self.board[x][y])
    
    def draw_ui(self):
        """UI 그리기"""
        # 배경
        pygame.draw.rect(screen, LIGHT_BROWN, (0, 0, SCREEN_WIDTH, 80))
        pygame.draw.rect(screen, DARK_BROWN, (0, 0, SCREEN_WIDTH, 80), 2)
        
        # 게임 정보
        if self.game_over:
            if self.winner:
                winner_text = "흑돌 승리!" if self.winner == 1 else "백돌 승리!"
                text_color = RED
            else:
                winner_text = "무승부!"
                text_color = BLUE
            text = self.font.render(winner_text, True, text_color)
        else:
            current_text = "흑돌 차례" if self.current_player == 1 else "백돌 차례"
            text_color = BLACK
            text = self.font.render(current_text, True, text_color)
        
        screen.blit(text, (20, 25))
        
        # 모드 및 난이도 표시
        mode_text = f"모드: {self.game_mode}"
        if self.game_mode == "AI":
            mode_text += f" (난이도: {self.ai_difficulty})"
        mode_surface = self.small_font.render(mode_text, True, BLACK)
        screen.blit(mode_surface, (20, 55))
        
        # 조작법 (게임이 끝나지 않았을 때만 표시)
        if not self.game_over:
            controls = [
                "R: 게임 재시작",
                "M: 모드 변경",
                "D: 난이도 변경",
                "S: 돌 이미지 설정",
                "ESC: 메뉴로"
            ]
            
            for i, control in enumerate(controls):
                control_surface = self.small_font.render(control, True, BLACK)
                screen.blit(control_surface, (SCREEN_WIDTH - 250, 20 + i * 20))
    
    def draw_game_over_menu(self):
        """게임 종료 후 메뉴 그리기"""
        # 반투명 배경
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        # 메뉴 박스
        menu_width = 400
        menu_height = 200
        menu_x = (SCREEN_WIDTH - menu_width) // 2
        menu_y = (SCREEN_HEIGHT - menu_height) // 2
        
        pygame.draw.rect(screen, LIGHT_BROWN, (menu_x, menu_y, menu_width, menu_height))
        pygame.draw.rect(screen, DARK_BROWN, (menu_x, menu_y, menu_width, menu_height), 3)
        
        # 제목
        title = self.font.render("게임 종료!", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, menu_y + 40))
        screen.blit(title, title_rect)
        
        # 버튼들
        buttons = ["다시 한 번 더?", "나갈래요"]
        for i, button_text in enumerate(buttons):
            color = RED if self.game_over_selection == i else BLACK
            button_surface = self.font.render(button_text, True, color)
            button_rect = button_surface.get_rect(center=(SCREEN_WIDTH//2, menu_y + 100 + i * 50))
            screen.blit(button_surface, button_rect)
    
    def draw_menu(self):
        """메뉴 화면 그리기"""
        # 배경
        screen.fill(LIGHT_BROWN)
        
        # 제목
        title = self.title_font.render("3D 오목 게임", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 150))
        screen.blit(title, title_rect)
        
        # 메뉴 옵션
        menu_options = [
            ("AI 대전", "AI"),
            ("2인 대전", "2P"),
            ("난이도 설정", "DIFFICULTY"),
            ("돌 선택", "STONE"),
            ("종료", "EXIT")
        ]
        
        for i, (text, value) in enumerate(menu_options):
            color = RED if self.menu_selection == i else BLACK
            option_surface = self.font.render(text, True, color)
            option_rect = option_surface.get_rect(center=(SCREEN_WIDTH//2, 300 + i * 50))
            screen.blit(option_surface, option_rect)
        
        # 난이도 설정 화면
        if self.menu_selection == 2:  # 난이도 설정 선택 시
            difficulty_text = f"현재 난이도: {self.ai_difficulty}"
            diff_surface = self.font.render(difficulty_text, True, BLUE)
            diff_rect = diff_surface.get_rect(center=(SCREEN_WIDTH//2, 500))
            screen.blit(diff_surface, diff_rect)
            
            difficulties = ["하", "중", "상"]
            for i, diff in enumerate(difficulties):
                color = RED if self.difficulty_selection == i else BLACK
                diff_option = self.small_font.render(diff, True, color)
                diff_rect = diff_option.get_rect(center=(SCREEN_WIDTH//2 - 100 + i * 100, 550))
                screen.blit(diff_option, diff_rect)
        
        # 돌 선택 화면
        elif self.menu_selection == 3:  # 돌 선택 선택 시
            stone_text = f"현재 선택: {self.available_stones[self.stone_selection]}"
            stone_surface = self.font.render(stone_text, True, BLUE)
            stone_rect = stone_surface.get_rect(center=(SCREEN_WIDTH//2, 500))
            screen.blit(stone_surface, stone_rect)
            
            # 돌 옵션들
            for i, stone_name in enumerate(self.available_stones):
                color = RED if self.stone_selection == i else BLACK
                stone_option = self.small_font.render(stone_name, True, color)
                stone_rect = stone_option.get_rect(center=(SCREEN_WIDTH//2 - 150 + i * 150, 550))
                screen.blit(stone_option, stone_rect)
            
            # 사용자 이미지 경로 표시
            if self.stone_selection == 2:
                path_text = f"경로: {self.custom_stone_path if self.custom_stone_path else '설정되지 않음'}"
                path_surface = self.small_font.render(path_text, True, BLACK)
                path_rect = path_surface.get_rect(center=(SCREEN_WIDTH//2, 580))
                screen.blit(path_surface, path_rect)
        
        # 설명
        instructions = [
            "방향키로 선택하고 Enter로 확인",
            "ESC: 게임 중 메뉴로 돌아가기"
        ]
        
        for i, instruction in enumerate(instructions):
            inst_surface = self.small_font.render(instruction, True, BLACK)
            inst_rect = inst_surface.get_rect(center=(SCREEN_WIDTH//2, 650 + i * 30))
            screen.blit(inst_surface, inst_rect)
    
    def get_board_position(self, mouse_x, mouse_y):
        """마우스 위치를 보드 좌표로 변환 (정확한 위치 계산)"""
        if (BOARD_OFFSET_X <= mouse_x <= BOARD_OFFSET_X + BOARD_SIZE * CELL_SIZE and
            BOARD_OFFSET_Y <= mouse_y <= BOARD_OFFSET_Y + BOARD_SIZE * CELL_SIZE):
            
            # 정확한 셀 위치 계산
            x = round((mouse_x - BOARD_OFFSET_X) / CELL_SIZE)
            y = round((mouse_y - BOARD_OFFSET_Y) / CELL_SIZE)
            
            # 범위 확인
            if 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE:
                return x, y
        return None
    
    def is_valid_move(self, x, y):
        """유효한 수인지 확인"""
        return self.board[x][y] == 0
    
    def make_move(self, x, y):
        """수 두기"""
        if self.is_valid_move(x, y):
            self.board[x][y] = self.current_player
            self.last_move = (x, y)
            
            # 사운드 재생
            if self.stone_sound:
                self.stone_sound.play()
            
            if self.check_win(x, y):
                self.game_over = True
                self.winner = self.current_player
                # 승리 효과
                if self.win_sound:
                    self.win_sound.play()
                center_x = BOARD_OFFSET_X + x * CELL_SIZE
                center_y = BOARD_OFFSET_Y + y * CELL_SIZE
                self.create_celebration(center_x, center_y)
                self.show_celebration = True
                self.celebration_timer = 180  # 3초 (60fps * 3)
                # 게임 종료 메뉴 표시
                self.show_game_over_menu = True
                self.game_over_selection = 0
            elif self.check_draw():
                self.game_over = True
                self.winner = None
                # 게임 종료 메뉴 표시
                self.show_game_over_menu = True
                self.game_over_selection = 0
            else:
                self.current_player = 3 - self.current_player  # 1->2, 2->1
            return True
        return False
    
    def check_win(self, x, y):
        """승리 조건 확인"""
        player = self.board[x][y]
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        
        for dx, dy in directions:
            count = 1
            
            # 양방향으로 확인
            for direction in [1, -1]:
                nx, ny = x, y
                for _ in range(4):
                    nx += dx * direction
                    ny += dy * direction
                    if (0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE and 
                        self.board[nx][ny] == player):
                        count += 1
                    else:
                        break
            
            if count >= 5:
                return True
        return False
    
    def check_draw(self):
        """무승부 확인"""
        return np.all(self.board != 0)
    
    def ai_move(self):
        """AI 수 두기"""
        if self.game_over:
            return
        
        # 지연 시간 확인
        current_time = pygame.time.get_ticks()
        if current_time - self.last_ai_time < self.ai_delay:
            return
        
        self.last_ai_time = current_time
        
        # 난이도에 따른 AI 전략
        empty_positions = []
        for x in range(BOARD_SIZE):
            for y in range(BOARD_SIZE):
                if self.board[x][y] == 0:
                    empty_positions.append((x, y))
        
        if empty_positions:
            if self.ai_difficulty == "하":
                # 하: 완전 랜덤
                x, y = random.choice(empty_positions)
            elif self.ai_difficulty == "중":
                # 중: 기본 전략
                priority_positions = []
                for x, y in empty_positions:
                    priority = 0
                    # 중앙 근처
                    center = BOARD_SIZE // 2
                    if abs(x - center) <= 3 and abs(y - center) <= 3:
                        priority += 10
                    # 기존 돌 근처
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            nx, ny = x + dx, y + dy
                            if (0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE and 
                                self.board[nx][ny] != 0):
                                priority += 1
                    
                    priority_positions.append((priority, x, y))
                
                priority_positions.sort(reverse=True)
                top_choices = priority_positions[:5]
                _, x, y = random.choice(top_choices)
            else:  # 상
                # 상: 고급 전략 (공격 + 방어)
                best_score = float('-inf')
                best_move = None
                
                for x, y in empty_positions:
                    # 임시로 수를 두고 평가
                    self.board[x][y] = self.ai_player
                    score = self.evaluate_position(x, y)
                    self.board[x][y] = 0
                    
                    if score > best_score:
                        best_score = score
                        best_move = (x, y)
                
                if best_move:
                    x, y = best_move
                else:
                    x, y = random.choice(empty_positions)
            
            self.make_move(x, y)
    
    def evaluate_position(self, x, y):
        """위치 평가 (고급 AI용)"""
        player = self.ai_player
        opponent = 3 - player if player is not None else 1
        score = 0
        
        # 공격 점수
        score += self.evaluate_direction(x, y, player) * 2
        
        # 방어 점수
        self.board[x][y] = opponent
        score += self.evaluate_direction(x, y, opponent)
        self.board[x][y] = player
        
        return score
    
    def evaluate_direction(self, x, y, player):
        """특정 방향의 점수 평가"""
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        total_score = 0
        
        for dx, dy in directions:
            count = 1
            blocked = 0
            
            # 양방향 확인
            for direction in [1, -1]:
                nx, ny = x, y
                for _ in range(4):
                    nx += dx * direction
                    ny += dy * direction
                    if (0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE):
                        if self.board[nx][ny] == player:
                            count += 1
                        elif self.board[nx][ny] != 0:
                            blocked += 1
                            break
                        else:
                            break
                    else:
                        blocked += 1
                        break
            
            # 점수 계산
            if count >= 5:
                total_score += 10000
            elif count == 4 and blocked == 0:
                total_score += 1000
            elif count == 3 and blocked == 0:
                total_score += 100
            elif count == 2 and blocked == 0:
                total_score += 10
        
        return total_score
    
    def reset_game(self):
        """게임 재시작"""
        self.board = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int)
        self.current_player = 1
        self.game_over = False
        self.winner = None
        self.last_move = None
        self.particles = []
        self.show_celebration = False
        self.celebration_timer = 0
        self.last_ai_time = 0
        self.show_game_over_menu = False
        self.game_over_selection = 0
    
    def toggle_mode(self):
        """게임 모드 변경"""
        self.game_mode = "2P" if self.game_mode == "AI" else "AI"
        self.ai_player = 2 if self.game_mode == "AI" else None
        self.reset_game()
    
    def change_difficulty(self):
        """AI 난이도 변경"""
        difficulties = ["하", "중", "상"]
        current_index = difficulties.index(self.ai_difficulty)
        self.ai_difficulty = difficulties[(current_index + 1) % 3]
    
    def set_custom_stone_path(self):
        """사용자 이미지 경로 설정"""
        # 간단한 경로 설정 (실제로는 파일 선택 다이얼로그가 필요)
        if self.stone_selection == 2:  # 사용자 이미지 선택 시
            # 기본 경로 설정
            self.custom_stone_path = "gomoku_re/BC_CARD_CI.svg"
            print(f"사용자 이미지 경로 설정: {self.custom_stone_path}")
            self.update_stone_images()
    
    def render(self):
        """화면 렌더링"""
        if self.show_menu:
            self.draw_menu()
        else:
            screen.fill(LIGHT_BROWN)
            self.draw_3d_board()
            self.draw_stones()
            self.draw_ui()
            
            # 폭죽 효과
            if self.show_celebration and self.celebration_timer > 0:
                self.draw_particles()
                self.celebration_timer -= 1
                if self.celebration_timer <= 0:
                    self.show_celebration = False
            
            # 게임 종료 메뉴
            if self.show_game_over_menu:
                self.draw_game_over_menu()
        
        pygame.display.flip()
    
    def run(self):
        """게임 메인 루프"""
        clock = pygame.time.Clock()
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.KEYDOWN:
                    if self.show_menu:
                        if event.key == pygame.K_UP:
                            self.menu_selection = (self.menu_selection - 1) % 5
                        elif event.key == pygame.K_DOWN:
                            self.menu_selection = (self.menu_selection + 1) % 5
                        elif event.key == pygame.K_LEFT and self.menu_selection == 2:
                            self.difficulty_selection = (self.difficulty_selection - 1) % 3
                            difficulties = ["하", "중", "상"]
                            self.ai_difficulty = difficulties[self.difficulty_selection]
                        elif event.key == pygame.K_RIGHT and self.menu_selection == 2:
                            self.difficulty_selection = (self.difficulty_selection + 1) % 3
                            difficulties = ["하", "중", "상"]
                            self.ai_difficulty = difficulties[self.difficulty_selection]
                        elif event.key == pygame.K_LEFT and self.menu_selection == 3:
                            self.stone_selection = (self.stone_selection - 1) % 4
                            self.update_stone_images()
                        elif event.key == pygame.K_RIGHT and self.menu_selection == 3:
                            self.stone_selection = (self.stone_selection + 1) % 4
                            self.update_stone_images()
                        elif event.key == pygame.K_RETURN:
                            if self.menu_selection == 0:  # AI 대전
                                self.game_mode = "AI"
                                self.ai_player = 2
                                self.show_menu = False
                                self.reset_game()
                            elif self.menu_selection == 1:  # 2인 대전
                                self.game_mode = "2P"
                                self.ai_player = None
                                self.show_menu = False
                                self.reset_game()
                            elif self.menu_selection == 2:  # 난이도 설정
                                pass  # 이미 설정됨
                            elif self.menu_selection == 3:  # 돌 선택
                                pass  # 이미 설정됨
                            elif self.menu_selection == 4:  # 종료
                                pygame.quit()
                                sys.exit()
                    else:
                        if event.key == pygame.K_ESCAPE:
                            self.show_menu = True
                        elif event.key == pygame.K_r:
                            self.reset_game()
                        elif event.key == pygame.K_m:
                            self.toggle_mode()
                        elif event.key == pygame.K_d:
                            self.change_difficulty()
                        elif event.key == pygame.K_s:
                            self.set_custom_stone_path()
                
                # 게임 종료 메뉴 키보드 처리
                if self.show_game_over_menu:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP:
                            self.game_over_selection = (self.game_over_selection - 1) % 2
                        elif event.key == pygame.K_DOWN:
                            self.game_over_selection = (self.game_over_selection + 1) % 2
                        elif event.key == pygame.K_RETURN:
                            if self.game_over_selection == 0:  # 다시 하기
                                self.reset_game()
                                self.show_game_over_menu = False
                            elif self.game_over_selection == 1:  # 나가기
                                self.show_menu = True
                                self.show_game_over_menu = False
                
                if event.type == pygame.MOUSEBUTTONDOWN and not self.show_menu and not self.show_game_over_menu:
                    if event.button == 1:  # 좌클릭
                        pos = self.get_board_position(event.pos[0], event.pos[1])
                        if pos:
                            if self.make_move(pos[0], pos[1]):
                                # AI 모드이고 AI 차례라면 지연 시간 설정
                                if (self.game_mode == "AI" and not self.game_over and 
                                    self.current_player == self.ai_player):
                                    self.last_ai_time = pygame.time.get_ticks()
            
            # AI 수 두기
            if (not self.show_menu and not self.game_over and not self.show_game_over_menu and 
                self.game_mode == "AI" and self.current_player == self.ai_player):
                self.ai_move()
            
            # 파티클 업데이트
            if self.show_celebration:
                self.update_particles()
            
            self.render()
            clock.tick(60)

if __name__ == "__main__":
    game = Gomoku3DLight()
    game.run() 