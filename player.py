import discord
from PIL import Image,ImageOps
import os
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageOps, ImageSequence

class Player:
    def __init__(self):
        self.SPEELS = ["LIGHTNING",
                      "MAGIC TORNADO",
                      "PIT",
                      "HEAL",
                      "ULTRA HEAL",
                      "THROW BOOK",
                      "ENERGY RESET",
                      "GUN",
                      "STAR",
                      "TRAIN",
                      "TREE",
                      "TORNADO",
                      "BLOCK ENERGY",
                      "TAKE ENERGY",
                      "BLOCK SHIELD",
                      "ADD SPELL",
                      "EXCHANGE",
                      "ENERGY BLOCKER"
                      ]
    
    @staticmethod
    def FindOut(name: str):
        """
        Daha pratik
        [emoji, style, açıklama, kullanılmış açıklama (biz), kullanılmış açıklama (düşman)]
        """

        match name:
            case "LIGHTNING": 
                emoji = "⚡"
                style = discord.ButtonStyle.success
                damage = 20
                energyDamage = 10
                description = f"Throws lightning at the enemy.\nDamage: {damage}\nEnergy Damage: {energyDamage}"
                usedDescription1 = "- You used Lightning" 
                usedDescription2 = "- Your enemy threw lightning at you"
            case "MAGIC TORNADO": 
                emoji = "🪄"
                style = discord.ButtonStyle.success
                damage = 30
                energyDamage = 20
                description = f"Sends a hose of magic to the enemy.\nDamage: {damage}\nEnergy Damage: {energyDamage}"
                usedDescription1 = "- You used Magic Tornado" 
                usedDescription2 = "- Your enemy threw a magical tornado"
            case "PIT": 
                emoji = "🍂"
                style = discord.ButtonStyle.success
                damage = 30
                energyDamage = 20
                description = f"The enemy falls into a pit\nDamage: {damage}\nEnergy Damage: {energyDamage}"
                usedDescription1 = "- You dug a pit under your enemy" 
                usedDescription2 = "- Your enemy dug a pit under you"
            case "HEAL": 
                emoji = "❤️‍🩹"
                style = discord.ButtonStyle.success
                giveHealth = 30
                description = f"Heals you\nHeals: {giveHealth}"
                usedDescription1 = "- You used heal. Your heal increased" 
                usedDescription2 = "- Your enemy used heal. Your enemy's heal increased"
            case "ULTRA HEAL": 
                emoji = "💊"
                style = discord.ButtonStyle.success
                giveHealth = 100
                description = f"Heals your enemy and you\nHeals: {giveHealth}"
                usedDescription1 = "- You used ultra heal. Your and your enemy's heal is full!"  
                usedDescription2 = "- Your enemy used ultra heal. Your and your enemy's heal is full!"
            case "THROW BOOK": 
                emoji = "📖"
                style = discord.ButtonStyle.success
                damage = 15
                energyDamage = 5
                description = f"Throws a book to your enemy. (Literally)\nDamage: {damage}\nEnergy Damage: {energyDamage}"
                usedDescription1 = "- You threw a book to your enemy. How pathetic."
                usedDescription2 = "- Your enemy throw a book to you."
            case "ENERGY RESET": 
                emoji = "🪫"
                style = discord.ButtonStyle.success
                energyDamage = 100
                description = f"Resets your and enemy's energy\nEnergy Damage: {energyDamage}"
                usedDescription1 = "- You have reset your enemy's energy."
                usedDescription2 = "- Your enemy have reset your energy."
            case "GUN": 
                emoji = "🔫"
                style = discord.ButtonStyle.success
                damage = 50
                description = f"You shoot your enemy with a gun. If your enemy uses a shield, you will take the damage. But you CAN'T use a shield (for no reason)\nDamage: {damage}\nEnergy Damage: {0}"
                usedDescription1 = ""
                usedDescription2 = ""
            case "STAR": 
                emoji = "🌟"
                style = discord.ButtonStyle.success
                damage = 20
                energyDamage = 30
                description = f"A shooting star hits your enemy\nDamage: {damage}\nEnergy Damage: {energyDamage}"
                usedDescription1 = "- You threw a shooting star at your enemy" 
                usedDescription2 = "- Your enemy threw a shooting star at you"
            case "TRAIN": 
                emoji = "🚄"
                style = discord.ButtonStyle.success
                damage = 40
                energyDamage = 10
                description = f"A train crashes into you and your enemy. You'd better use a shield.\nDamage: {damage}\nEnergy Damage: {energyDamage}"
                usedDescription1 = "- The train arrives, choo-choo"
                usedDescription2 = "- Your enemy... Train... What the??"
            case "TREE": 
                emoji = "🌳"
                style = discord.ButtonStyle.success
                damage = 20
                energyDamage = 10
                description = f"A tree suddenly grows from under your enemy and throws him into the space (fr).\nDamage: {damage}\nEnergy Damage: {energyDamage}"
                usedDescription1 = "- You suddenly grew a tree under your enemy (You'd better be a farmer)" 
                usedDescription2 = "- Your enemy suddenly grew a tree under you."
            case "TORNADO": 
                emoji = "🌪️"
                style = discord.ButtonStyle.success
                damage = 20
                energyDamage = 20
                description = f"A real tornado picks up your enemy and goes away\nDamage: {damage}\nEnergy Damage: {energyDamage}"
                usedDescription1 = "- You used a *REAL* tornado"
                usedDescription2 = "- Your enemy used a tornado."
            case "BLOCK SPELL": 
                emoji = "✖️"
                style = discord.ButtonStyle.success
                damage = 30
                energyDamage = 20
                description = f"You can remove a spell of enemy's randomly"
                usedDescription1 = "- You deleted a spell of your enemy" 
                usedDescription2 = "- Your enemy deleted a spell of you. Poor you."
            case "TAKE ENERGY":
                emoji = "🔋"
                style = discord.ButtonStyle.success
                giveEnergy = 30
                description = f"Gives you 30 energy\nGives Energy: {giveEnergy}"
                usedDescription1 = "- You get 30 energy" 
                usedDescription2 = "- Your enemy get 30 energy" 
            case "BLOCK SHIELD": 
                emoji = "🛡️"
                style = discord.ButtonStyle.success
                damage = 30
                energyDamage = 20
                description =  f"You prevent your enemy from using his shield for 2 tour.\nDamage: {damage}\nEnergy Damage: {energyDamage}"
                usedDescription1 = "- You blocked your enemy's shield for 2 tour" 
                usedDescription2 = "- Your enemy blocked your shield for 2 tour. Sorry for that" 
            case "ADD SPELL": 
                emoji = "🔮"
                style = discord.ButtonStyle.success
                description = f"You add 2 random spell to yourself"
                usedDescription1 = "- You get new spells! Yeyy" 
                usedDescription2 = "- Your enemy get new spells! Opss" 
            case "EXCHANGE": 
                emoji = "👁️"
                style = discord.ButtonStyle.success
                description = f"You can exchange your enemy's spells for your own."
                usedDescription1 = "- Exchange!" 
                usedDescription2 = "- Your enemy made an exchange. Say goodbye to your spells" 
            case "ENERGY BLOCKER": 
                emoji = "🪄"
                style = discord.ButtonStyle.success
                description = f"Even if your enemy gains energy, he cannot use his energy for 3 turns"
                usedDescription1 = "- You blocked your enemy's energy for 3 tour. Now's your shot!" 
                usedDescription2 = "- You can't use your energy for 3 tour." 
            case _:
                emoji = "🪄"
                style = discord.ButtonStyle.red
                description = f"Bişeyler yanlış"
                usedDescription1 = f"1 {name}"  
                usedDescription2 = f"2 {name}" 

        return [emoji, style, description, usedDescription1, usedDescription2]
    
    @staticmethod
    def GetGIF(SpellName1: str, SpellName2: str, player: int = 1, Gun: bool = False) -> str:
        path = "C:\\Users\\EbuZe\\Desktop\\Colin\\Discord-Game-Bot-v1\\GIFS"

        def TakePath(name: str):
            match name:
                case "LIGHTNING": 
                    return "Ligthning.gif"
                case "MAGIC TORNADO": 
                    return "MagicTornado.gif"
                case "PIT": 
                    return "Pit.gif"
                case "HEAL": 
                    return "Heal.gif"
                case "ULTRA HEAL": 
                    return "UltraHeal.gif"
                case "THROW BOOK": 
                    return "ThrowBook.gif"
                case "ENERGY RESET": 
                    return "EnergyReset.gif"
                case "GUN": 
                    return "Gun1.gif" if Gun else "Gun2.gif"
                case "STAR": 
                    return "Star.gif"
                case "TRAIN": 
                    return "Train.gif"
                case "TREE": 
                    return "Tree.gif"
                case "TORNADO": 
                    return "Tornado.gif"
                case "BLOCK SPELL": 
                    return "BlockSpell.gif"
                case "TAKE ENERGY":
                    return "TakeEnergy.gif"
                case "BLOCK SHIELD": 
                    return "BlockShield.gif"
                case "ADD SPELL": 
                    return "AddSpell.gif"
                case "EXCHANGE": 
                    return "Exchange.gif"
                case "ENERGY BLOCKER": 
                    return "BlockEnergy.gif"
                case _:
                    print("Invalid Spell Name")
                    return None

        def mirror_gif(gifPath):
            # Open the GIF file
            gif_path = gifPath
            gif = Image.open(gif_path)

            # Create a list to hold mirrored frames
            frames = []

            # Iterate over each frame in the GIF
            while True:
                try:
                    # Mirror the frame (flip horizontally)
                    mirrored_frame = ImageOps.mirror(gif.copy())
                    frames.append(mirrored_frame)
                    gif.seek(gif.tell() + 1)
                except EOFError:
                    # End of GIF frames
                    break

            # Save the mirrored frames as a new GIF
            frames[0].save(f"{path}\\mirrored_gif{player}.gif", save_all=True, append_images=frames[1:], loop=0, duration=gif.info['duration'])

            return path + "\\" + f"mirrored_gif{player}.gif"

        return [discord.File(f"{path}\\" + TakePath(SpellName1)), discord.File(mirror_gif(f"{path}\\" + TakePath(SpellName2)))]

    def TakeDamage(MinHealth: int, Health: int, Damage: int):
        # Ekstra hesaplamalar yapmayı unutma
        Extract = Health - Damage

        if Extract > MinHealth:
            return Health - Damage
        
        return MinHealth
    
    def Heal(MaxHealth: int, Health: int, Heal: int) -> int:
        Plus = Health + Heal

        if MaxHealth < Plus:
            return MaxHealth
        
        return Plus
