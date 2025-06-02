import pygame
import random
import sys
import os

pygame.font.init()
pygame.init()

ProjectPath = sys.path[0]

AuraPath = os.path.join(ProjectPath, "Aura")
AssetsPath = os.path.join(ProjectPath, "Assets")
BackgroundsPath = os.path.join(ProjectPath, "Backgrounds")

Display = pygame.display
Draw = pygame.draw
Clock = pygame.time.Clock()
Mixer = pygame.mixer.music

Screen = Display.set_mode((1080, 720), pygame.RESIZABLE)

FrameRate = 60
DeltaTime = 1 / FrameRate

LuckMultiplier = 0.75
RollCooldown = 0.5
AuraDropTime = 0.1
AuraClearWait = 1
RollCooldownWait = AuraClearWait

RollStatusTextPos = 20
AuraHeightDrop = 50
AuraHeightSize = 75
RollImageSize = 2

CanRoll = True
RarestAura = 0
AuraList = []
CooldownTime = 4

for Item in os.listdir(AuraPath):
	Rarity = int(Item.replace(".png", ""))

	if Rarity > RarestAura:
		RarestAura = Rarity
	
	AuraList.append([os.path.join(AuraPath, Item), Rarity])

def SortList(Value):
	return -Value[1]

AuraList.sort(key=SortList)

def Roll():
	RNG = int(random.random() * RarestAura)

	for Aura in AuraList:
		if RNG % int(Aura[1] / LuckMultiplier) == 0:
			return Aura
	
	return AuraList[len(AuraList) - 1]

ScreenRect = Screen.get_rect()

AuraImage = None
AuraImagePos = None
BackgroundImage = pygame.image.load(os.path.join(BackgroundsPath, "Background1.png")).convert()
BackgroundRect = BackgroundImage.get_rect()

BackgroundScale = max(ScreenRect[2] / BackgroundRect[2], ScreenRect[3] / BackgroundRect[3])

BackgroundImage = pygame.transform.scale(BackgroundImage, (
	int(BackgroundRect[2] * BackgroundScale), 
	int(BackgroundRect[3] * BackgroundScale)
))

BackgroundRect = BackgroundImage.get_rect(center=ScreenRect.center)

RollImage = pygame.image.load(os.path.join(AssetsPath, "Roll.png")).convert()
RollImageRect = RollImage.get_rect()

RollImage = pygame.transform.scale(RollImage, (RollImageRect[2] * RollImageSize, RollImageRect[3] * RollImageSize))
RollImageRect = RollImage.get_rect()

RollImagePos = ((ScreenRect[2] * 0.5) - (RollImageRect[2] / 2), ScreenRect[3] - RollImageRect[3] - 25)
RollImageRect.topleft = RollImagePos

CooldownFrame = pygame.Surface((RollImageRect[2], RollImageRect[3]), pygame.SRCALPHA)
CooldownFrame.fill((255, 255, 255, 127))

RollBackground = pygame.Surface((ScreenRect[2], ScreenRect[3]), pygame.SRCALPHA)
RollBackground.fill((27, 27, 27, 127))

RollText = pygame.image.load(os.path.join(AssetsPath, "RollStatus.png")).convert_alpha()

MainFont = pygame.font.SysFont(os.path.join(AssetsPath, "SourceSans3-Regular.ttf"), 30)
ChanceText = None

def BlitAll():
	global CooldownFrame, AuraImage, AuraImagePos, ChanceText

	Screen.blit(BackgroundImage, (0, 0))

	if AuraImage:
		AuraImageRect = AuraImage.get_rect()

		Screen.blit(RollBackground, (0, 0))
		Screen.blit(AuraImage, AuraImagePos)

		TextRect = ChanceText.get_rect()

		Screen.blit(ChanceText, (
			(AuraImagePos[0] + (AuraImageRect[2] / 2)) - (TextRect[2] / 2),
			(AuraImagePos[1] + AuraImageRect[3]) + 10
		))

		TextRect = RollText.get_rect()

		Screen.blit(RollText, (
			(ScreenRect[2] / 2) - (TextRect[2] / 2),
			RollStatusTextPos
		))
	else:
		Screen.blit(RollImage, RollImagePos)
		Screen.blit(CooldownFrame, RollImagePos)

BlitAll()

while True:
	Events = pygame.event.get()
	ViewportX, ViewportY = Screen.get_size()

	for Event in Events:
		if Event.type == pygame.QUIT:
			pygame.quit()
		
		if Event.type == pygame.MOUSEBUTTONUP and CanRoll:
			if not RollImageRect.collidepoint(Event.pos):
				continue
				
			CooldownTime = 0
			RolledAura = Roll()

			CanRoll = False
			ChanceText = MainFont.render(f'1 in {RolledAura[1]}', False, (255, 255, 255))

			AuraImage = pygame.image.load(RolledAura[0]).convert_alpha()
			AuraRect = AuraImage.get_rect()
				
			SizeMultiplier = AuraHeightSize / AuraRect[3]

			AuraImage = pygame.transform.scale(AuraImage, (AuraRect[2] * SizeMultiplier, AuraRect[3] * SizeMultiplier))

	CooldownPercent = max(min(1 - ((CooldownTime - RollCooldownWait) / RollCooldown), 1), 0)	

	CooldownFrame = pygame.transform.scale(CooldownFrame, (
		max(RollImageRect[2] * CooldownPercent, 1), 
		RollImageRect[3]
	))

	if CooldownPercent == 0:
		CanRoll = True

	if CooldownTime >= AuraClearWait and AuraImage:
		AuraImage = None
	elif AuraImage:
		AuraImageRect = AuraImage.get_rect()
		AuraImagePos = (
			(ScreenRect[2] / 2) - (AuraImageRect[2] / 2), 
			(ScreenRect[3] / 2) - (AuraImageRect[3] / 2) + (max(min((CooldownTime / AuraDropTime), 1), 0) * AuraHeightDrop) - AuraHeightDrop, 
		)
	
	BlitAll()

	pygame.display.flip()
	DeltaTime = Clock.tick(FrameRate) / 1000
	CooldownTime += DeltaTime
