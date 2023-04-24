import pygame
from pygame import mixer
import random

pygame.init()
pygame.font.init()
pygame.mixer.init()

#define window size
Screen_Width = 1200
Screen_Height = 681

#Fonts
clock_font = pygame.font.SysFont('Verdana', 20)
popup_font = pygame.font.SysFont('Verdana', 30)
money_font = pygame.font.SysFont('Verdana', 28)

#Colours
BG = (144, 201, 120)
White = (255, 255, 255)
Black = (0, 0, 0)
Red = (255, 0, 0)
Money_Yellow = (250, 250, 3)
Beige = (227,218,201)
Orange = (255, 165, 0)
Yellow = (255, 255, 0)
Green = (0, 128, 0)

#Create Game Screen
screen = pygame.display.set_mode((Screen_Width, Screen_Height))
pygame.display.set_caption('Energy Island')

#Create Clock
clock = pygame.time.Clock()

# Set the initial time value
start_time = pygame.time.get_ticks()

# Set the time converter
month_factor = 15000  # 15 seconds (10000 milliseconds) in real life per month in game
year_factor = 12 * month_factor  # 12 months per year
last_month_updated = 0
last_month = -1
current_time = pygame.time.get_ticks()
current_month = (current_time - start_time) // month_factor
current_year = current_month // 12


#Backgroud Sounds

#Background Images
Island = pygame.image.load('Assets/Background.png')
Settlement = pygame.image.load('Assets/Settlement.png')
Forest = pygame.image.load('Assets/Forest.png')
Tidal = pygame.image.load('Assets/Tidal.png')
Volcano = pygame.image.load('Assets/Volcano.png')
Solar = pygame.image.load('Assets/Solar.png')
Offshore = pygame.image.load('Assets/Offshore.png')
Onshore = pygame.image.load('Assets/Onshore.png')
Oilrig = pygame.image.load('Assets/Oilrig.png')
Coalmine = pygame.image.load('Assets/Coalmine.png')
WIN = pygame.image.load('Assets/Win.png')
LOSS = pygame.image.load('Assets/Loss.png')

#Button Images
start_img = pygame.image.load('Assets/start_but.png').convert_alpha()
exit_img = pygame.image.load('Assets/exit_but.png').convert_alpha()
#restart_img = pygame.image.load('Assets/restart_but.png').convert_alpha()

#Create Button Class
class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False
        self.visible = True
        
    def draw(self):
        action = False
        #check mouseover and clicks
        if self.visible and self.rect.collidepoint(pygame.mouse.get_pos()):
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                self.clicked = True
                action = True       
        #hide button if clicked
        if not self.visible or self.clicked:
            return False
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
        #draw button
        screen.blit(self.image, (self.rect.x, self.rect.y))
        return action
    
#Create Pop-Up Window Class
class PopUp:
    def __init__(self, text, font_size=30, color=Black, bg_color=Beige, alpha=280, rect_size=(450, 350)):
        self.font = pygame.font.SysFont('Verdana', font_size)
        self.text = text.split('\n')
        self.text_surfaces = [self.font.render(line, True, color) for line in self.text]
        self.rect = pygame.Rect((Screen_Width - rect_size[0]) // 2, (Screen_Height - rect_size[1]) // 2, rect_size[0], rect_size[1])
        self.bg = pygame.Surface((self.rect.width, self.rect.height))
        self.bg.fill(bg_color)
        self.bg.set_alpha(alpha)
        
    def draw(self, surface):
        surface.blit(self.bg, self.rect)
        total_text_height = sum(text_surface.get_height() for text_surface in self.text_surfaces)
        y_offset = (self.rect.height - total_text_height) // 2
        for text_surface in self.text_surfaces:
            text_rect = text_surface.get_rect(center=(self.rect.centerx, self.rect.top + y_offset + text_surface.get_height() // 2))
            surface.blit(text_surface, text_rect)
            y_offset += text_surface.get_height()
        
    def check_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                return False
        return True
        
#create button instances
start_button = Button(Screen_Width // 2 - 130, Screen_Height // 2 - 150, start_img)
exit_button = Button(Screen_Width // 2 - 110, Screen_Height // 2 + 50, exit_img)
#restart_button = Button(Screen_Width // 2 - 100, Screen_Height // 2 - 50, restart_img)

#Earnings
budget_values = [100]
#settlement
num_turbines = 0
turbines = []
turbine_cost = 30
turbine_earnings = 10  # calculate the monthly earnings with interest
#forest
num_forests = 0
forests = []
forest_cost = 45
forest_earnings = 10
#tidal
num_tidals = 0
tidals = []
tidal_cost = 70
tidal_earnings = 15
#volcano
num_volcanos = 0
volcanos = []
volcano_cost = 80
volcano_earnings = 15
#solar
num_solars = 0
solars = []
solar_cost = 275
solar_earnings = 25
#offshore
num_offshores = 0
offshores = []
offshore_cost = 210
offshore_earnings = 20
#onshore
num_onshores = 0
onshores = []
onshore_cost = 180
onshore_earnings = 20

assets = ['Turbine', 'Forest', 'Tidal', 'Volcano', 'Solar', 'Offshore', 'Onshore']
bought_assets = []



#Progress bar
renewable_energy_percentage = 0
turbines_purchased = 0
forests_purchased = 0
tidals_purchased = 0
volcanos_purchased = 0
solars_purchased = 0
offshores_purchased = 0
onshores_purchased = 0
bar_width = 200
bar_height = 20
bar_x = 10
bar_y = 10
total_reductions = 0
renewable_energy_percentage = (num_turbines+num_forests+num_tidals+num_volcanos+num_solars+num_offshores+num_onshores) * 0.5
def get_renewable_energy_color():
    if renewable_energy_percentage <25:
        return Red
    elif renewable_energy_percentage < 50:
        return Orange
    elif renewable_energy_percentage < 75:
        return Yellow
    else:
        return Green
    
def update_renewable_energy_percentage():
    global renewable_energy_percentage
    global total_reductions
    global deduct_oil_rig_investment
    global deduct_coal_mine_investment
    renewable_energy_percentage = 0
    for turbine in turbines:
        months_owned = turbine['payments']
        percentage_per_turbine = 0.5*(months_owned + 1)
        renewable_energy_percentage += percentage_per_turbine
    for forest in forests:
        months_owned = forest['payments']
        percentage_per_forest = 0.7*(months_owned + 1)
        renewable_energy_percentage += percentage_per_forest
    for tidal in tidals:
        months_owned = tidal['payments']
        percentage_per_tidal = 0.9*(months_owned + 1)
        renewable_energy_percentage += percentage_per_tidal
    for volcano in volcanos:
        months_owned = volcano['payments']
        percentage_per_volcano = (months_owned + 1)
        renewable_energy_percentage += percentage_per_volcano
    for solar in solars:
        months_owned = solar['payments']
        percentage_per_solar = 1.4*(months_owned + 1)
        renewable_energy_percentage += percentage_per_solar
    for offshore in offshores:
        months_owned = offshore['payments']
        percentage_per_offshore = 1.3*(months_owned + 1)
        renewable_energy_percentage += percentage_per_offshore
    for onshore in onshores:
        months_owned = onshore['payments']
        percentage_per_onshore = 1.1*(months_owned + 1)
        renewable_energy_percentage += percentage_per_onshore
    renewable_energy_percentage = min(renewable_energy_percentage - total_reductions, 100) #doesn't exceed 100
    if deduct_oil_rig_investment:
        renewable_energy_percentage -= 10
        total_reductions += 10
        deduct_oil_rig_investment = False
    elif deduct_coal_mine_investment:
        renewable_energy_percentage -= 25
        total_reductions += 25
        deduct_coal_mine_investment = False
    
def draw_progress_bar(surface):
    # Calculate progress bar width based on percentage
    bar_progress = bar_width * renewable_energy_percentage / 100
    
    # Draw progress bar outline
    pygame.draw.rect(surface, Black, (bar_x, bar_y, bar_width, bar_height), 1)
    
    # Draw progress bar fill
    pygame.draw.rect(surface, get_renewable_energy_color(), (bar_x, bar_y, bar_progress, bar_height))
    
    # Draw progress bar text
    font = pygame.font.SysFont(None, 20)
    text = font.render(f"{round(renewable_energy_percentage,1)}%", True, Black)
    surface.blit(text, (bar_x + bar_width + 10, bar_y))
    

#-------------------
#-------------------
#-------------------
#-------------------

#minigame   
    
trivia_img = pygame.image.load('Assets/Minigame.png')
trivia_rect = trivia_img.get_rect()
x_position = 45
y_position = 80
trivia_rect.topleft = (x_position, y_position)

questions_answered = 0

questions = [
    {
        "question": "What is the primary source of energy for Earth's climate system?",
        "answers": ["Geothermal energy", "Fossil fuels", "Solar energy", "Wind energy"],
        "correct": 2,
    },
    {
        "question": "Which of the following is a non-renewable energy source?",
        "answers": ["Wind energy", "Solar energy", "Hydropower", "Natural gas"],
        "correct": 3,
    },
    {
        "question": "Which country has the largest installed capacity of wind energy?",
        "answers": ["China", "United States", "Russia", "Denmark"],
        "correct": 0,
    },
    {
        "question": "What type of energy is derived from the Earth's internal heat?",
        "answers": ["Wind energy", "Geothermal energy", "Hydropower", "Solar energy"],
        "correct": 1,
    },
    {
        "question": "Which of the following is NOT a type of biomass?",
        "answers": ["Algae", "Wood", "Agricultural Waste", "Oil"],
        "correct": 3,
    },
    {
        "question": "Which of the following is NOT an example of a fossil fuel?",
        "answers": ["Oil", "Wood", "Natural Gas", "Coal"],
        "correct": 1,
    },
    {
        "question": "What is the energy conversion process used by solar panels?",
        "answers": ["Photovoltaic", "Electrochemical", "Thermodynamic", "Hydroelectric"],
        "correct": 0,
    },
    {
        "question": "Which of these energy sources is not considered renewable?",
        "answers": ["Nuclear power", "Solar power", "Hydropower", "Wind power"],
        "correct": 0,
    },
    {
        "question": "What is the main greenhouse gas emitted by burning fossil fuels?",
        "answers": ["Methane", "Carbon dioxide", "Nitrous oxide", "Ozone"],
        "correct": 1,
    },
    {
        "question": "What do we call energy from the movement of air?",
        "answers": ["Solar energy", "Wind energy", "Geothermal energy", "Hydro energy"],
        "correct": 1,
    },
    {
        "question": "What type of energy is stored in a battery?",
        "answers": ["Chemical energy", "Thermal energy", "Electromagnetic energy", "Kinetic energy"],
        "correct": 0,
    },
    {
        "question": "Which of the following is an example of renewable energy?",
        "answers": ["Gasoline", "Diesel", "Kerosene", "Biodiesel"],
        "correct": 3,
    },
    {
        "question": "Which energy source can produce electricity without burning fuel?",
        "answers": ["Coal", "Natural gas", "Solar power", "Oil"],
        "correct": 2,
    },
    {
        "question": "What energy source is stored underground and formed from ancient plant?",
        "answers": ["Solar energy", "Fossil fuels", "Hydropower", "Wind energy"],
        "correct": 1,
    },
    {
        "question": "What type of energy do plants use to create food?",
        "answers": ["Wind energy", "Solar energy", "Geothermal energy", "Hydro energy"],
        "correct": 1,
    },
    {
        "question": "What type of energy is produced when atoms are split or combined?",
        "answers": ["Nuclear energy", "Chemical energy", "Mechanical energy", "Electrical energy"],
        "correct": 0,
    },
    {
        "question": "Which of the following is an example of a biofuel?",
        "answers": ["Diesel", "Gasoline", "Ethanol", "Natural gas"],
        "correct": 2,
    },
    {
        "question": "What is the process by which plants convert sunlight into energy?",
        "answers": ["Respiration", "Photosynthesis", "Fermentation", "Digestion"],
        "correct": 1,
    },
    {
        "question": "Which of these energy sources is not considered renewable?",
        "answers": ["Nuclear power", "Solar power", "Hydropower", "Wind power"],
        "correct": 0,
    },
    {
        "question": "What is the energy transformation that occurs in a solar panel?",
        "answers": ["Chemical to electrical", "Light to electrical", "Mechanical to electrical", "Thermal to electrical"],
        "correct": 1,
    },
    {
        "question": "Which type of power plant uses steam to spin a turbine and generate electricity?",
        "answers": ["Nuclear power plant", "Solar power plant", "Wind farm", "Hydroelectric dam"],
        "correct": 0,
    },
    {
        "question": "What is the term for the ability to do work or cause change?",
        "answers": ["Force", "Power", "Energy", "Matter"],
        "correct": 2,
    },
    {
        "question": "What type of energy source does not contribute to air pollution?",
        "answers": ["Fossil fuels", "Nuclear power", "Wind power", "Coal"],
        "correct": 2,
    },
    {
        "question": "What is the energy transformation that occurs in a wind turbine?",
        "answers": ["Chemical to mechanical", "Light to electrical", "Mechanical to electrical", "Thermal to electrical"],
        "correct": 2,
    },
    {
        "question": "What is the fundamental principle of the conservation of energy?",
        "answers": ["Energy can be created from nothing","Energy can be destroyed completely","Energy can neither be created nor destroyed","Energy can be both created and destroyed"],
        "correct": 2,
    }
    # Add more questions
]




#-------------------
#-------------------
#-------------------
#-------------------

#minigame

#Allow to click on island areas
click_enabled = False

#starting money
money = 100

run = True
show_island = False
show_popup_settlement_first_click = False
time_constraint = 2
show_popup_time_constraint = False
show_popup_settlement_first_click_2 = False
show_settlement = False
show_forest = False
show_tidal = False
show_volcano = False
show_solar = False
show_offshore = False
show_onshore = False
show_oilrig = False
show_coalmine = False
tutorial_settlement = True
bought_settlement = False
bought_forest = False
bought_tidal = False
bought_volcano = False
bought_solar = False
bought_offshore = False
bought_onshore = False
show_popup = True
show_graph = False
show_popup_explore_island = False
popup_low_budget = False
show_natural_disaster =False
initial_click = True
x = ['drought', 'tsunami', 'flood', 'hail storm', 'earthquake', 'tornado']
current_disaster = None
trivia_mini_game = False
question_data = None
answer_selected = False
correct_popup = False
after_game = False
after_win = False
after_loss = False
oil_rig_event = False
show_popup_oil_rig_investment = False
deduct_oil_rig_investment = False
coal_mine_event = False
show_popup_coal_mine_investment = False
deduct_coal_mine_investment = False

pygame.mixer.music.load("Assets/Lobby-Time.mp3")
pygame.mixer.music.play(-1) 

while run:
                
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False #if quit, the pygame window closes
            
        if event.type == pygame.MOUSEBUTTONDOWN:  # check mouse click events
            if start_button.rect.collidepoint(pygame.mouse.get_pos()):  # check start button click
                start_button.visible = False
                exit_button.visible = False
                show_island = True #shows island if start is clicked
            elif exit_button.rect.collidepoint(pygame.mouse.get_pos()):  # check exit button click
                run = False
                
            if click_enabled and (current_month >= 1 or current_year >= 1) and not tutorial_settlement:
                if trivia_rect.collidepoint(pygame.mouse.get_pos()) and not trivia_mini_game:
                    trivia_mini_game = True
                    click_enabled = False
                    if questions:
                        question_data = random.choice(questions)
                        #questions.remove(question_data)
                        questions_answered = 0
            
                
        #introduction pop-ups
                
        if show_popup and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE: #first intro
            show_popup = False  # hide pop-up when spacebar is pressed
            click_enabled = True #allow to press on areas of island
            
        elif show_popup_settlement_first_click and not show_popup_settlement_first_click_2 and tutorial_settlement and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE: #settlement intro
            show_popup_settlement_first_click = False  # hide pop-up when spacebar is pressed
            show_popup_time_constraint = True
            
        elif show_popup_time_constraint and tutorial_settlement and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            show_popup_time_constraint = False
            show_popup_settlement_first_click_2 = True
        
        elif show_popup_settlement_first_click_2 and tutorial_settlement and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:  #Another settlement intro
            show_popup_settlement_first_click_2 = False
            show_settlement = True
            
        #settlement purchase page
        
        elif show_settlement and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE: #Settlement buy page close down
            show_settlement = False
            click_enabled = True
            
        elif show_settlement and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: #Settlement buy page purchase
            area_pos = pygame.mouse.get_pos()
            if pygame.Rect(715, 389, 200, 124).collidepoint(area_pos): #Buy-button on Settlement
                if money >= turbine_cost:
                    money -= turbine_cost
                    num_turbines += 1
                    turbine = {'type': 'Turbine', 'index': num_turbines, 'cost': turbine_cost, 'payments': 0, 'balance': -turbine_cost}
                    turbines.append(turbine)
                    bought_assets.append(turbine)
                    update_renewable_energy_percentage()
                    show_settlement = False
                    bought_settlement = True
                    initial_click = False
                    
                else:
                    show_settlement = False
                    popup_low_budget = True
                    
        elif bought_settlement and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE: #Pop-up if settlement bought
            bought_settlement = False
            if tutorial_settlement == True:
                show_popup_explore_island = True
            elif tutorial_settlement == False:
                click_enabled = True
            
        elif show_popup_explore_island and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            show_popup_explore_island = False
            tutorial_settlement = False
            click_enabled = True    
        
        #forest purchase page
                    
        elif show_forest and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            show_forest = False
            click_enabled = True
            
        elif show_forest and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            area_pos = pygame.mouse.get_pos()
            if pygame.Rect(715, 365, 200, 125).collidepoint(area_pos):
                if money >= forest_cost:
                    money -= forest_cost
                    num_forests += 1
                    forest = {'type': 'Forest', 'index': num_forests, 'cost': forest_cost, 'payments': 0, 'balance': -forest_cost}
                    forests.append(forest)
                    bought_assets.append(forest)
                    update_renewable_energy_percentage()
                    show_forest = False
                    bought_forest = True
                else:
                    show_forest = False
                    popup_low_budget = True
                    
        elif bought_forest and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                bought_forest = False
                click_enabled = True
                
        #tidal purchase page
        
        elif show_tidal and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            show_tidal = False
            click_enabled = True
            
        elif show_tidal and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            area_pos = pygame.mouse.get_pos()
            if pygame.Rect(260, 400, 200, 125).collidepoint(area_pos):
                if money >= tidal_cost:
                    money -= tidal_cost
                    num_tidals += 1
                    tidal = {'type': 'Tidal', 'index': num_tidals, 'cost': tidal_cost, 'payments': 0, 'balance': -tidal_cost}
                    tidals.append(tidal)
                    bought_assets.append(tidal)
                    update_renewable_energy_percentage()
                    show_tidal = False
                    bought_tidal = True
                else:
                    show_tidal = False
                    popup_low_budget = True
                    
        elif bought_tidal and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                bought_tidal = False
                click_enabled = True
        
        #volcano
        
        elif show_volcano and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            show_volcano = False
            click_enabled = True
            
        elif show_volcano and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            area_pos = pygame.mouse.get_pos()
            if pygame.Rect(350, 420, 200, 125).collidepoint(area_pos):
                if money >= volcano_cost:
                    money -= volcano_cost
                    num_volcanos += 1
                    volcano = {'type': 'Volcano', 'index': num_volcanos, 'cost': volcano_cost, 'payments': 0, 'balance': -volcano_cost}
                    volcanos.append(volcano)
                    bought_assets.append(volcano)
                    update_renewable_energy_percentage()
                    show_volcano = False
                    bought_volcano = True
                else:
                    show_volcano = False
                    popup_low_budget = True
                    
        elif bought_volcano and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                bought_volcano = False
                click_enabled = True
        
        #solar
        
        elif show_solar and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            show_solar = False
            click_enabled = True
            
        elif show_solar and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            area_pos = pygame.mouse.get_pos()
            if pygame.Rect(710, 383, 200, 125).collidepoint(area_pos):
                if money >= solar_cost:
                    money -= solar_cost
                    num_solars += 1
                    solar = {'type': 'Solar', 'index': num_solars, 'cost': solar_cost, 'payments': 0, 'balance': -solar_cost}
                    solars.append(solar)
                    bought_assets.append(solar)
                    update_renewable_energy_percentage()
                    show_solar = False
                    bought_solar = True
                else:
                    show_solar = False
                    popup_low_budget = True
                    
        elif bought_solar and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                bought_solar = False
                click_enabled = True
        
        #Offshore
        
        elif show_offshore and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            show_offshore = False
            click_enabled = True
            
        elif show_offshore and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            area_pos = pygame.mouse.get_pos()
            if pygame.Rect(650, 383, 200, 125).collidepoint(area_pos):
                if money >= offshore_cost:
                    money -= offshore_cost
                    num_offshores += 1
                    offshore = {'type': 'Offshore', 'index': num_offshores, 'cost': offshore_cost, 'payments': 0, 'balance': -offshore_cost}
                    offshores.append(offshore)
                    bought_assets.append(offshore)
                    update_renewable_energy_percentage()
                    show_offshore = False
                    bought_offshore = True
                else:
                    show_offshore = False
                    popup_low_budget = True
                    
        elif bought_offshore and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                bought_offshore = False
                click_enabled = True
                
        #Onshore
        
        elif show_onshore and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            show_onshore = False
            click_enabled = True
            
        elif show_onshore and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            area_pos = pygame.mouse.get_pos()
            if pygame.Rect(650, 383, 200, 125).collidepoint(area_pos):
                if money >= onshore_cost:
                    money -= onshore_cost
                    num_onshores += 1
                    onshore = {'type': 'Onshore', 'index': num_onshores, 'cost': onshore_cost, 'payments': 0, 'balance': -onshore_cost}
                    onshores.append(onshore)
                    bought_assets.append(onshore)
                    update_renewable_energy_percentage()
                    show_onshore = False
                    bought_onshore = True
                else:
                    show_onshore = False
                    popup_low_budget = True
                    
        elif bought_onshore and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                bought_onshore = False
                click_enabled = True
                
        #Oilrig
        
        elif show_oilrig and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                show_oilrig = False
                click_enabled = True
                
        #Coalmine
        
        elif show_coalmine and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                show_coalmine = False
                click_enabled = True
                      
        #Too little money to buy
        elif popup_low_budget and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                popup_low_budget = False
                click_enabled = True
            
        #Too much money
        elif show_natural_disaster and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            show_natural_disaster = False
            click_enabled = True
            
        #Fossil fuel investments
        elif show_popup_oil_rig_investment and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            show_popup_oil_rig_investment = False
            click_enabled = True
        
        elif show_popup_coal_mine_investment and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            show_popup_coal_mine_investment = False
            click_enabled = True
        
        
        #clicking actions
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and click_enabled:
            area_pos = pygame.mouse.get_pos()
            
            if pygame.Rect(630, 70, 150, 80).collidepoint(area_pos) and not initial_click: #Forest
                click_enabled = False
                show_forest = True
                
            elif pygame.Rect(557, 289, 112, 98).collidepoint(area_pos) and tutorial_settlement: #Settlement
                click_enabled = False
                show_popup_settlement_first_click = True             
                
            elif pygame.Rect(557, 289, 112, 98).collidepoint(area_pos) and not tutorial_settlement: #No Tutorial Settlement
                click_enabled = False
                show_settlement = True
                                  
            elif pygame.Rect(772, 438, 70, 87).collidepoint(area_pos) and not initial_click: #Off-shore
                click_enabled = False
                show_offshore = True
                
            elif pygame.Rect(387, 181, 80, 89).collidepoint(area_pos) and not initial_click: #On-Shore
                click_enabled = False
                show_onshore = True
                
            elif pygame.Rect(400, 351, 99, 102).collidepoint(area_pos) and not initial_click: #Solar farm
                click_enabled = False
                show_solar = True
                
            elif pygame.Rect(861, 214, 115, 43).collidepoint(area_pos) and not initial_click: #Tidal farm
                click_enabled = False
                show_tidal = True
                
            elif pygame.Rect(163, 270, 105, 82).collidepoint(area_pos) and not initial_click: #Oil rig
                click_enabled = False
                show_oilrig = True
                
            elif pygame.Rect(533, 147, 67, 63).collidepoint(area_pos) and not initial_click: #Coal mine
                click_enabled = False
                show_coalmine = True
                
            elif pygame.Rect(487, 492, 81, 87).collidepoint(area_pos) and not initial_click: #Volcano
                click_enabled = False
                show_volcano = True
                
            #progress bar click
    
    time_elapsed = pygame.time.get_ticks() - start_time
    years = time_elapsed // year_factor
    months = int((time_elapsed % year_factor) // month_factor)
        
    if months != last_month_updated:
        last_month_updated = months
        for turbine in turbines:
            turbine['payments'] += 1
            turbine['balance'] += turbine_earnings
            money += turbine_earnings
            budget_values.append(money)
        for forest in forests:
            forest['payments'] += 1
            forest['balance'] += forest_earnings
            money += forest_earnings
            budget_values.append(money)
        for tidal in tidals:
            tidal['payments'] += 1
            tidal['balance'] += tidal_earnings
            money += tidal_earnings
            budget_values.append(money)
        for volcano in volcanos:
            volcano['payments'] += 1
            volcano['balance'] += volcano_earnings
            money += volcano_earnings
            budget_values.append(money)
        for solar in solars:
            solar['payments'] += 1
            solar['balance'] += solar_earnings
            money += solar_earnings
            budget_values.append(money)
        for offshore in offshores:
            offshore['payments'] += 1
            offshore['balance'] += offshore_earnings
            money += offshore_earnings
            budget_values.append(money)
        for onshore in onshores:
            onshore['payments'] += 1
            onshore['balance'] += onshore_earnings
            money += onshore_earnings
            budget_values.append(money)
        if money >= 500 and not after_game:
            money = 0
            budget_values.append(money)
            current_disaster = random.choice(x)
            show_natural_disaster = True
        update_renewable_energy_percentage()
            

    clock_text = clock_font.render(f"Month: {months}  Year: {years}", True, pygame.Color('forestgreen'))
    
    screen.fill(BG)
    if show_island:  #if == True
        screen.blit(Island, (0, 0))
        screen.blit(clock_text, (1000, 640))
        money_text = money_font.render(f"Budget:  ${money}", True, Money_Yellow)
        screen.blit(money_text, (980, 20))
        draw_progress_bar(screen)
        
        
        for i, item in enumerate(bought_assets):
            asset = item['type']
            text = money_font.render(f"{asset} {item['index']}: ${item['balance']}", True, Money_Yellow)
            screen.blit(text, (980, 80 + i * 30))
        
            
        if show_popup:  # if == True
            popup = PopUp("Welcome to Energy Island!\n\nBegin by clicking on the settlement.\n\n\nPress SPACE to continue", font_size=25, color=Black, bg_color=Beige, alpha=280)
            popup.draw(screen)  # draw popup
        if show_popup_settlement_first_click:
            popup = PopUp("We are so happy you have come\nto save our island from the evil\nfossil fuel company!\n\nYou will help us make our energy\ncleaner and save us from the\nconsequences of using oil and coal\nas an energy source.\n\n\nClick SPACE to continue.", font_size=25, color=Black, bg_color=Beige, alpha=280)
            popup.draw(screen)
        if show_popup_time_constraint:
            popup = PopUp(f"But please hurry!\nWe only have {time_constraint} years before\nthe fossil fuel company wins!\n\nIf you do not manage to have\n100% progress by then,\nthe game will be lost.\n\n\nClick SPACE to continue.", font_size=25, color=Black, bg_color=Beige, alpha=280)
            popup.draw(screen)
        if show_popup_settlement_first_click_2:
            popup = PopUp("Did you know...?\n\nThe use of fossil fuel energy is\none of the main reasons for\nclimate change today.\n\nThis can increase global temperatures,\nmelt icebergs, raise sea-levels\nand ultimately sink our island!\n\n\nClick SPACE to continue.", font_size=25, color=Black, bg_color=Beige, alpha=280)
            popup.draw(screen)
        if show_popup_explore_island:
            popup = PopUp("Now continue to help the islanders\nby exploring the island and\npurchasing renewable energy plants.\n\n\nPress SPACE to continue", font_size=25, color=Black, bg_color=Beige, alpha=280)
            popup.draw(screen)
            
        if show_settlement:
            screen.blit(Settlement, (200, 81))
        if bought_settlement:
            popup = PopUp(f"Congratulations!\nYou built a small wind-turbine!\n\nYou spent ${turbine_cost} and will earn\n${turbine_earnings} per month.\n\n\nPress SPACE to continue", font_size=25, color=Black, bg_color=Beige, alpha=280)
            popup.draw(screen)
            
        if show_forest:
            screen.blit(Forest, (200, 81))
        if bought_forest:
            popup = PopUp(f"Congratulations!\nYou built a biomass power plant!\n\nYou spent ${forest_cost} and will earn\n${forest_earnings} per month.\n\n\nPress SPACE to continue", font_size=25, color=Black, bg_color=Beige, alpha=280)
            popup.draw(screen)
            
        if show_tidal:
            screen.blit(Tidal, (200, 81))
        if bought_tidal:
            popup = PopUp(f"Congratulations!\nYou built a tidal power station!\n\nYou spent ${tidal_cost} and will earn\n${tidal_earnings} per month.\n\n\nPress SPACE to continue", font_size=25, color=Black, bg_color=Beige, alpha=280)
            popup.draw(screen)
            
        if show_volcano:
            screen.blit(Volcano, (200, 81))
        if bought_volcano:
            popup = PopUp(f"Congratulations!\nYou built a geothermal energy plant!\n\nYou spent ${volcano_cost} and will earn\n${volcano_earnings} per month.\n\n\nPress SPACE to continue", font_size=25, color=Black, bg_color=Beige, alpha=280)
            popup.draw(screen)
        
        if show_solar:
            screen.blit(Solar, (200, 81))
        if bought_solar:
            popup = PopUp(f"Congratulations!\nYou built a solar farm!\n\nYou spent ${solar_cost} and will earn\n${solar_earnings} per month.\n\n\nPress SPACE to continue", font_size=25, color=Black, bg_color=Beige, alpha=280)
            popup.draw(screen)
            
        if show_offshore:
            screen.blit(Offshore, (200, 81))
        if bought_offshore:
            popup = PopUp(f"Congratulations!\nYou built an off-shore wind farm!\n\nYou spent ${offshore_cost} and will earn\n${offshore_earnings} per month.\n\n\nPress SPACE to continue", font_size=25, color=Black, bg_color=Beige, alpha=280)
            popup.draw(screen)
        
        if show_onshore:
            screen.blit(Onshore, (200, 81))
        if bought_onshore:
            popup = PopUp(f"Congratulations!\nYou built an on-shore wind farm!\n\nYou spent ${onshore_cost} and will earn\n${onshore_earnings} per month.\n\n\nPress SPACE to continue", font_size=25, color=Black, bg_color=Beige, alpha=280)
            popup.draw(screen)
            
        if show_oilrig:
            screen.blit(Oilrig, (200, 81))
            
        if show_coalmine:
            screen.blit(Coalmine, (200, 81))
            
        #low budget
        if popup_low_budget:
            popup = PopUp("Sorry your budget is too low\nto purchase this.\nTry explore more areas of the island,\nor wait until your budget has increased.\n\n\nPress SPACE to continue", font_size=25, color=Black, bg_color=Beige, alpha=280)
            popup.draw(screen)  # draw popup
            
        #too much money
            
        if show_natural_disaster:
            click_enabled = False
            popup = PopUp(f"Oh no! You've had to spend\nyour entire budget on reperations\ndue to a {current_disaster}.\n\n\nPress SPACE to continue", font_size=25, color=Black, bg_color=Beige, alpha=280)
            popup.draw(screen)
            
        current_time = pygame.time.get_ticks()
        current_month = (current_time - start_time) // month_factor
        current_year = current_month // 12
            
        #win game
        if renewable_energy_percentage >= 100 and not after_loss:
            click_enabled = False
            after_win = True
            after_game = True
            screen.blit(WIN, (200, 81))
            
        #lose game
        if current_year >= 2  and not after_win:
            click_enabled = False
            after_loss = True
            after_game = True
            screen.blit(LOSS, (200, 81))
            
        #fossil fuel investments
        if years == 0 and months == 8 and click_enabled and not oil_rig_event:
            oil_rig_event = True
            deduct_oil_rig_investment = True
            update_renewable_energy_percentage()
            show_popup_oil_rig_investment = True
            click_enabled = False
            
        if show_popup_oil_rig_investment:
            popup = PopUp("The fossil fuel company invested\nin a new oil rig.\n\nYour progress has decreased by 10%.\n\n\nPress SPACE to continue", font_size=25, color=Black, bg_color=Beige, alpha=280)
            popup.draw(screen)
            
        if years == 1 and months == 4 and click_enabled and not coal_mine_event:
            coal_mine_event = True
            deduct_coal_mine_investment = True
            update_renewable_energy_percentage()
            show_popup_coal_mine_investment = True
            click_enabled = False
            
        if show_popup_coal_mine_investment:
            popup = PopUp("The fossil fuel company invested\nin a new coal mine.\n\nYour progress has decreased by 25%.\n\n\nPress SPACE to continue", font_size=25, color=Black, bg_color=Beige, alpha=280)
            popup.draw(screen)
    
    #--------------- 
    #--------------- 
    #---------------
        
    #Mini-game
        
        if click_enabled and (current_month >= 2 or current_year >= 1):
            screen.blit(trivia_img, trivia_rect.topleft)

        if trivia_mini_game and question_data:
            pink_rect = pygame.Rect(150, 80, 900, 520)
            pygame.draw.rect(screen, (244,194,194), pink_rect)

            num_correct_this_game = 0

            question_text = clock_font.render(question_data['question'], True, (0, 0, 0))
            screen.blit(question_text, (340, 180))

            answer_rects = []
            answer_texts = []
            for i, answer in enumerate(question_data['answers']):
                answer_rect = pygame.Rect(350, 250 + i * 50, 500, 30)
                answer_rects.append(answer_rect)
                pygame.draw.rect(screen, (255, 255, 255), answer_rect)
                answer_text = clock_font.render(answer, True, (0, 0, 0))
                answer_texts.append(answer_text)
                screen.blit(answer_text, (360, 257 + i * 50))

            answer_selected = False
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and not answer_selected:
                    for i, answer_rect in enumerate(answer_rects):
                        if answer_rect.collidepoint(pygame.mouse.get_pos()):
                            if i == question_data['correct']:
                                pygame.draw.rect(screen, (0, 255, 0), answer_rect)  # Light up green
                                num_correct_this_game += 1

                            else:
                                pygame.draw.rect(screen, (255, 0, 0), answer_rect)  # Light up red
                                correct_rect = answer_rects[question_data['correct']]
                                pygame.draw.rect(screen, (0, 255, 0), correct_rect)  # Light up the correct answer green

                            # Draw the answer text again to make it visible over colours
                            for i, answer_text in enumerate(answer_texts):
                                screen.blit(answer_text, (360, 257 + i * 50))

                            message_text = clock_font.render("Press SPACE to continue", True, (0, 0, 0))
                            screen.blit(message_text, (400, 500))
                            pygame.display.flip()

                            questions_answered += 1
                            answer_selected = True                 

                while answer_selected:
                    for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                            if questions_answered < 4 and questions:
                                question_data = random.choice(questions)
                                trivia_mini_game = True
                                answer_selected = False
                            else:
                                #correct_popup = True
                                trivia_mini_game = False
                                click_enabled = True
                                answer_selected = False
                                answer_selected = False
                                question_data = None
                                questions_answered = 0
                                
        #---------------
        #---------------
        #---------------        
        draw_progress_bar(screen)
    start_button.draw()
    exit_button.draw()
    
    pygame.display.update()
    clock.tick(60)

pygame.quit()
