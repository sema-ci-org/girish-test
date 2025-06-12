import random
import time
import sys
from enum import Enum
from typing import List, Dict, Optional, Tuple, Any, Union

# Type definitions for better code clarity
Type = Enum('Type', [
    'NORMAL', 'FIRE', 'WATER', 'ELECTRIC', 'GRASS', 'ICE',
    'FIGHTING', 'POISON', 'GROUND', 'FLYING', 'PSYCHIC',
    'BUG', 'ROCK', 'GHOST', 'DRAGON', 'DARK', 'STEEL', 'FAIRY'
])

class Stats:
    def __init__(self, hp: int, attack: int, defense: int, sp_attack: int, sp_defense: int, speed: int):
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.sp_attack = sp_attack
        self.sp_defense = sp_defense
        self.speed = speed
    
    def __str__(self) -> str:
        return (
            f"HP: {self.hp}\n"
            f"Attack: {self.attack}\n"
            f"Defense: {self.defense}\n"
            f"Sp. Atk: {self.sp_attack}\n"
            f"Sp. Def: {self.sp_defense}\n"
            f"Speed: {self.speed}"
        )

class Move:
    def __init__(self, name: str, move_type: Type, power: int, accuracy: int, pp: int,
                 category: str = 'physical', effect: Optional[callable] = None):
        self.name = name
        self.move_type = move_type
        self.power = power
        self.accuracy = accuracy
        self.pp = pp
        self.max_pp = pp
        self.category = category
        self.effect = effect
    
    def use(self) -> bool:
        if self.pp <= 0:
            print(f"No PP left for {self.name}!")
            return False
        self.pp -= 1
        return True
    
    def __str__(self) -> str:
        return f"{self.name} ({self.move_type.name}) - Power: {self.power}, PP: {self.pp}/{self.max_pp}"

class Pokemon:
    def __init__(self, name: str, pokemon_type: List[Type], level: int, base_stats: Stats,
                 moves: List[Move]):
        self.name = name
        self.types = pokemon_type
        self.level = level
        self.base_stats = base_stats
        self.current_hp = self.calculate_stat(base_stats.hp)
        self.stats = self.calculate_stats()
        self.moves = moves
        self.status = None
        self.status_turns = 0
        self.fainted = False
    
    def calculate_stat(self, base_stat: int, iv: int = 31, ev: int = 0) -> int:
        # Simplified stat calculation
        return ((2 * base_stat + iv + (ev // 4)) * self.level // 100) + 5
    
    def calculate_stats(self) -> Dict[str, int]:
        return {
            'hp': self.calculate_stat(self.base_stats.hp) + self.level + 10,
            'attack': self.calculate_stat(self.base_stats.attack),
            'defense': self.calculate_stat(self.base_stats.defense),
            'sp_attack': self.calculate_stat(self.base_stats.sp_attack),
            'sp_defense': self.calculate_stat(self.base_stats.sp_defense),
            'speed': self.calculate_stat(self.base_stats.speed)
        }
    
    def take_damage(self, damage: int) -> None:
        self.current_hp = max(0, self.current_hp - damage)
        if self.current_hp == 0:
            self.faint()
    
    def heal(self, amount: int) -> None:
        max_hp = self.stats['hp']
        self.current_hp = min(max_hp, self.current_hp + amount)
    
    def faint(self) -> None:
        self.fainted = True
        print(f"{self.name} fainted!")
    
    def is_fainted(self) -> bool:
        return self.fainted
    
    def get_move(self, move_name: str) -> Optional[Move]:
        for move in self.moves:
            if move.name.lower() == move_name.lower():
                return move
        return None
    
    def show_moves(self) -> None:
        print(f"\n{self.name}'s moves:")
        for i, move in enumerate(self.moves, 1):
            print(f"{i}. {move}")
    
    def __str__(self) -> str:
        type_str = "/".join(t.name for t in self.types)
        hp_bar_length = 20
        hp_percent = (self.current_hp / self.stats['hp']) * 100
        hp_bar = '█' * int(hp_bar_length * (hp_percent / 100))
        hp_bar += ' ' * (hp_bar_length - len(hp_bar))
        
        return (
            f"{self.name} (Lv. {self.level}) - {type_str}\n"
            f"HP: [{hp_bar}] {self.current_hp}/{self.stats['hp']}\n"
            f"Status: {self.status if self.status else 'Normal'}"
        )

class Trainer:
    def __init__(self, name: str):
        self.name = name
        self.pokemon_team: List[Pokemon] = []
        self.current_pokemon: Optional[Pokemon] = None
        self.items = {
            'potion': 3,
            'super potion': 1,
            'revive': 1
        }
    
    def add_pokemon(self, pokemon: Pokemon) -> None:
        if len(self.pokemon_team) < 6:
            self.pokemon_team.append(pokemon)
            if len(self.pokemon_team) == 1:
                self.current_pokemon = pokemon
            print(f"{pokemon.name} was added to {self.name}'s team!")
        else:
            print("Your team is full!")
    
    def switch_pokemon(self, index: int) -> bool:
        if 0 <= index < len(self.pokemon_team):
            if self.pokemon_team[index].is_fainted():
                print(f"{self.pokemon_team[index].name} is fainted and can't battle!")
                return False
            if self.pokemon_team[index] == self.current_pokemon:
                print(f"{self.current_pokemon.name} is already in battle!")
                return False
            
            print(f"{self.name} withdrew {self.current_pokemon.name} and sent out {self.pokemon_team[index].name}!")
            self.current_pokemon = self.pokemon_team[index]
            return True
        return False
    
    def has_usable_pokemon(self) -> bool:
        return any(not pokemon.is_fainted() for pokemon in self.pokemon_team)
    
    def use_item(self, item_name: str, target: Pokemon) -> bool:
        item_name = item_name.lower()
        if item_name not in self.items or self.items[item_name] <= 0:
            print(f"No {item_name} left!")
            return False
        
        if item_name == 'potion':
            heal_amount = 20
            target.heal(heal_amount)
            print(f"{target.name} recovered {heal_amount} HP!")
        elif item_name == 'super potion':
            heal_amount = 50
            target.heal(heal_amount)
            print(f"{target.name} recovered {heal_amount} HP!")
        elif item_name == 'revive':
            if target.is_fainted():
                target.fainted = False
                target.current_hp = target.stats['hp'] // 2
                print(f"{target.name} was revived with {target.current_hp} HP!")
            else:
                print("Can only revive fainted Pokémon!")
                return False
        
        self.items[item_name] -= 1
        return True
    
    def show_team(self) -> None:
        print(f"\n{self.name}'s team:")
        for i, pokemon in enumerate(self.pokemon_team, 1):
            status = ""
            if pokemon.is_fainted():
                status = " (FAINTED)"
            elif pokemon == self.current_pokemon:
                status = " (IN BATTLE)"
            print(f"{i}. {pokemon.name} - HP: {pokemon.current_hp}/{pokemon.stats['hp']}{status}")
    
    def show_items(self) -> None:
        print(f"\n{self.name}'s items:")
        for item, count in self.items.items():
            print(f"- {item.title()}: {count}")

class Battle:
    def __init__(self, player: Trainer, opponent: Trainer):
        self.player = player
        self.opponent = opponent
        self.turn = 0
    
    def start_battle(self) -> None:
        print(f"\nA wild {self.opponent.current_pokemon.name} appeared!")
        print(f"Go! {self.player.current_pokemon.name}!")
        
        while True:
            self.turn += 1
            print(f"\n--- Turn {self.turn} ---")
            
            # Check for battle end conditions
            if not self.player.has_usable_pokemon():
                print("You lost the battle!")
                break
            if not self.opponent.has_usable_pokemon():
                print("You won the battle!")
                break
            
            # Get player action
            player_action = self.get_player_action()
            
            # Get opponent action (AI)
            opponent_action = self.get_ai_action()
            
            # Determine turn order based on speed
            player_first = (
                self.player.current_pokemon.stats['speed'] >=
                self.opponent.current_pokemon.stats['speed']
            )
            
            # Execute actions in speed order
            if player_first:
                self.execute_action(self.player, self.opponent, player_action)
                if not self.opponent.current_pokemon.is_fainted():
                    self.execute_action(self.opponent, self.player, opponent_action)
            else:
                self.execute_action(self.opponent, self.player, opponent_action)
                if not self.player.current_pokemon.is_fainted():
                    self.execute_action(self.player, self.opponent, player_action)
    
    def get_player_action(self) -> str:
        while True:
            print("\nWhat will you do?")
            print("1. Fight")
            print("2. Switch Pokémon")
            print("3. Use Item")
            print("4. Run")
            
            choice = input("Choose an option (1-4): ")
            
            if choice == '1':
                return self.choose_move()
            elif choice == '2':
                if self.switch_pokemon():
                    return 'switch'
            elif choice == '3':
                if self.use_item():
                    return 'item'
            elif choice == '4':
                print("Got away safely!")
                exit()
            else:
                print("Invalid choice. Try again.")
    
    def choose_move(self) -> str:
        self.player.current_pokemon.show_moves()
        while True:
            try:
                move_num = int(input("Choose a move (1-4): ")) - 1
                if 0 <= move_num < len(self.player.current_pokemon.moves):
                    move = self.player.current_pokemon.moves[move_num]
                    if move.pp > 0:
                        return f'move {move.name}'
                    else:
                        print("No PP left for this move!")
                else:
                    print("Invalid move number!")
            except ValueError:
                print("Please enter a number!")
    
    def switch_pokemon(self) -> bool:
        self.player.show_team()
        while True:
            try:
                choice = input("Choose a Pokémon to switch to (1-6) or 'c' to cancel: ")
                if choice.lower() == 'c':
                    return False
                
                pokemon_num = int(choice) - 1
                if 0 <= pokemon_num < len(self.player.pokemon_team):
                    if self.player.switch_pokemon(pokemon_num):
                        return True
                else:
                    print("Invalid Pokémon number!")
            except ValueError:
                print("Please enter a number!")
    
    def use_item(self) -> bool:
        self.player.show_items()
        while True:
            item = input("Choose an item to use or 'c' to cancel: ").lower()
            if item == 'c':
                return False
            
            if item in self.player.items and self.player.items[item] > 0:
                if self.player.current_pokemon.is_fainted() and item != 'revive':
                    print(f"Can't use {item} on a fainted Pokémon!")
                    continue
                
                if item == 'revive' and not self.player.current_pokemon.is_fainted():
                    print("Can only use Revive on fainted Pokémon!")
                    continue
                
                self.player.use_item(item, self.player.current_pokemon)
                return True
            else:
                print("Invalid item or none left!")
    
    def get_ai_action(self) -> str:
        # Simple AI: 80% chance to attack, 20% chance to use an item if available
        if random.random() < 0.8 or not self.ai_has_usable_item():
            # Choose a random move that has PP left
            available_moves = [m for m in self.opponent.current_pokemon.moves if m.pp > 0]
            if available_moves:
                move = random.choice(available_moves)
                return f'move {move.name}'
        
        # Try to use an item
        if self.ai_use_item():
            return 'item'
        
        # If no items can be used, use the first available move
        available_moves = [m for m in self.opponent.current_pokemon.moves if m.pp > 0]
        if available_moves:
            move = available_moves[0]
            return f'move {move.name}'
        
        # If all else fails, struggle
        return 'move Struggle'
    
    def ai_has_usable_item(self) -> bool:
        return any(count > 0 for item, count in self.opponent.items.items())
    
    def ai_use_item(self) -> bool:
        # Simple AI item usage logic
        if self.opponent.current_pokemon.current_hp < self.opponent.current_pokemon.stats['hp'] // 2:
            if self.opponent.items.get('potion', 0) > 0:
                self.opponent.use_item('potion', self.opponent.current_pokemon)
                return True
            elif self.opponent.items.get('super potion', 0) > 0:
                self.opponent.use_item('super potion', self.opponent.current_pokemon)
                return True
        
        for pokemon in self.opponent.pokemon_team:
            if pokemon.is_fainted() and self.opponent.items.get('revive', 0) > 0:
                self.opponent.use_item('revive', pokemon)
                return True
        
        return False
    
    def execute_action(self, user: Trainer, target_trainer: Trainer, action: str) -> None:
        if action.startswith('move '):
            move_name = action[5:]
            move = user.current_pokemon.get_move(move_name)
            if move and move.use():
                self.use_move(user.current_pokemon, target_trainer.current_pokemon, move)
        elif action == 'switch':
            print(f"{user.name} switched Pokémon!")
        elif action == 'item':
            print(f"{user.name} used an item!")
    
    def use_move(self, attacker: Pokemon, defender: Pokemon, move: Move) -> None:
        print(f"{attacker.name} used {move.name}!")
        
        # Check for miss
        if random.randint(1, 100) > move.accuracy:
            print("But it missed!")
            return
        
        # Calculate damage (simplified)
        attack_stat = attacker.stats['attack'] if move.category == 'physical' else attacker.stats['sp_attack']
        defense_stat = defender.stats['defense'] if move.category == 'physical' else defender.stats['sp_defense']
        
        # STAB (Same Type Attack Bonus)
        stab = 1.5 if move.move_type in attacker.types else 1.0
        
        # Type effectiveness (simplified)
        effectiveness = 1.0
        for t in defender.types:
            # This is a simplified type chart
            if (move.move_type == Type.FIRE and t in [Type.GRASS, Type.ICE, Type.BUG]) or \
               (move.move_type == Type.WATER and t in [Type.FIRE, Type.GROUND, Type.ROCK]) or \
               (move.move_type == Type.ELECTRIC and t in [Type.WATER, Type.FLYING]):
                effectiveness *= 2.0
            elif (move.move_type == Type.FIRE and t in [Type.WATER, Type.ROCK, Type.DRAGON]) or \
                 (move.move_type == Type.WATER and t in [Type.WATER, Type.GRASS, Type.DRAGON]) or \
                 (move.move_type == Type.ELECTRIC and t in [Type.ELECTRIC, Type.GRASS, Type.DRAGON]):
                effectiveness *= 0.5
            elif (move.move_type == Type.NORMAL and t == Type.ROCK) or \
                 (move.move_type == Type.FIGHTING and t == Type.GHOST):
                effectiveness = 0
        
        if effectiveness == 0:
            print("It had no effect!")
            return
        elif effectiveness > 1.0:
            print("It's super effective!")
        elif effectiveness < 1.0:
            print("It's not very effective...")
        
        # Critical hit (simplified)
        critical = 1.5 if random.random() < 0.1 else 1.0
        if critical > 1.0:
            print("A critical hit!")
        
        # Calculate damage (simplified formula)
        level_factor = (2 * attacker.level) / 5 + 2
        damage = int((level_factor * move.power * attack_stat / defense_stat) / 50 + 2)
        damage = int(damage * stab * effectiveness * critical * random.uniform(0.85, 1.0))
        
        # Apply damage
        defender.take_damage(damage)
        print(f"{defender.name} took {damage} damage!")
        
        # Check if the move has an additional effect
        if move.effect:
            move.effect(attacker, defender)

# Create some moves
tackle = Move("Tackle", Type.NORMAL, 40, 100, 35)
ember = Move("Ember", Type.FIRE, 40, 100, 25)
water_gun = Move("Water Gun", Type.WATER, 40, 100, 25)
thunder_shock = Move("Thunder Shock", Type.ELECTRIC, 40, 100, 30)
vine_whip = Move("Vine Whip", Type.GRASS, 45, 100, 25)
flamethrower = Move("Flamethrower", Type.FIRE, 90, 100, 15)
surf = Move("Surf", Type.WATER, 90, 100, 15)
thunderbolt = Move("Thunderbolt", Type.ELECTRIC, 90, 100, 15)
solar_beam = Move("Solar Beam", Type.GRASS, 120, 100, 10)

# Create some Pokémon
charmander = Pokemon(
    "Charmander",
    [Type.FIRE],
    10,
    Stats(39, 52, 43, 60, 50, 65),
    [tackle, ember, flamethrower]
)

squirtle = Pokemon(
    "Squirtle",
    [Type.WATER],
    10,
    Stats(44, 48, 65, 50, 64, 43),
    [tackle, water_gun, surf]
)

bulbasaur = Pokemon(
    "Bulbasaur",
    [Type.GRASS, Type.POISON],
    10,
    Stats(45, 49, 49, 65, 65, 45),
    [tackle, vine_whip, solar_beam]
)

pikachu = Pokemon(
    "Pikachu",
    [Type.ELECTRIC],
    10,
    Stats(35, 55, 40, 50, 50, 90),
    [tackle, thunder_shock, thunderbolt]
)

# Create trainers
player = Trainer("Ash")
player.add_pokemon(charmander)
player.add_pokemon(squirtle)
player.add_pokemon(bulbasaur)

rival = Trainer("Gary")
rival.add_pokemon(pikachu)

# Add some items to the rival
rival.items = {
    'potion': 2,
    'super potion': 1,
    'revive': 1
}

def main():
    print("Welcome to Pokémon!")
    print("1. Start New Game")
    print("2. Exit")
    
    while True:
        choice = input("Choose an option (1-2): ")
        
        if choice == '1':
            battle = Battle(player, rival)
            battle.start_battle()
            break
        elif choice == '2':
            print("Thanks for playing!")
            sys.exit()
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()