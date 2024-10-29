import discord
from discord import Embed
from discord.ui import button, Button, View
from discord.ext import commands, tasks
import sqlite3
import random
import os
import asyncio
from player import Player

class Game(View):
    def __init__(self, 
                 MainInteraction: discord.Interaction, 
                 player1: discord.Member, 
                 player2: discord.Member, 
                 usingFor:str,
                 OldGameObject: View = None): 
        """
        VERİ TABANINA DAHA İYİ ULAŞMAK VE OYUNU DAHA İYİ YÖNETMEK İÇİN BİR SINIF
    
        MainInteraction: Ana interaction değerini alır
        player1: 1. oyuncunun değerlerini taşır.
        player2: 2. oyuncunun değerlerini taşır.

        - MainInteraction ile her zaman ana mesaja ulaşabiliriz
        - player1 ve player2 aynı tür olduğu için iki saat tür ayarlaması yapmaya gerek yok.
        - usingFor ile bu sınıfı nasıl kontrol edebileceğimizi bulabiliriz:
            HOST --> Başlangıç Ayarları
            ACorReF --> Daveti kabul etme
            Game1 --> Oyuncu 1 İçin
            Game2 --> Oyuncu 2 için
        """
        super().__init__()

        self.MainInteraction = MainInteraction
        self.SecondInteraction: discord.Interaction
        self.player1 = player1
        self.player2 = player2

        self.connection = sqlite3.connect("database.db")
        self.cursor = self.connection.cursor()

        self.MaxHealth = 100
        self.MaxEnergy = 100
        self.MaxShieldHealth = 100
        self.SpellListLength = 6

        self.starterColumnCount = 19

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
                      "BLOCK SPELL",
                      "TAKE ENERGY",
                      "BLOCK SHIELD",
                      "ADD SPELL",
                      "EXCHANGE",
                      "ENERGY BLOCKER"
                      ]
        
        match usingFor:
            case "HOST":
                self.HostGame()
            case "ACorReF":
                self.AcceptOrRefuse()
            case "Game1":
                self.Game(player=self.player1)
            case "Game2":
                self.Game(player=self.player2)

    # VERİ TABANI FONKSİYONLARI

    def CreateData(self, SpellListLength:int, player1: discord.Member, player2: discord.Member):
        a = ""
        for i in range(1, SpellListLength+1):
            if i == SpellListLength: a += f"Spell{i} TEXT"
            else: a += f"Spell{i} TEXT,\n\t"
                
        self.cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS Users (
        guild_id INTEGER,
        user_id INTEGER,
        IsInGame INTEGER,
        IsPlayed INTEGER,
        MaxHealth INTEGER,
        Health INTEGER,
        MaxEnergy INTEGER,
        Energy INTEGER,
        MaxShieldHealth INTEGER,
        ShieldHealth INTEGER,
        IsShieldOn INTEGER,
        NoUsingValueBecauseWhyNot INTEGER,
        ExtraDamage INTEGER,
        CanSee INTEGER,
        WaitTour INTEGER,
        EnergyAmount INTEGER,
        EnergyBlock INTEGER,
        ShieldBlock INTEGER,
        UsedSpell TEXT,
        {a}
        ) ''')

        '''
        guild_id INTEGER, 0
        user_id INTEGER, 1
        IsInGame INTEGER, 2
        IsPlayed INTEGER 3
        MaxHealth INTEGER, 4
        Health INTEGER, 5
        MaxEnergy INTEGER, 6
        Energy INTEGER, 7
        MaxShieldHealth INTEGER, 8
        ShieldHealth INTEGER, 9
        IsShieldOn INTEGER, 10
        EnergyAmount INTEGER, 11
        ExtraDamage Integer, 12
        CanSee INTEGER, 13
        WaitTour INTEGER, 14
        EnergyAmount INTEGER, 15
        EnergyBlock,    16
        ShieldBlock     17
        UsedSpell       18
        {a}
        '''

        self.connection.commit()

        self.RegisterPlayer(player=player1)
        self.RegisterPlayer(player=player2)

    def RegisterPlayer(self, player: discord.Member):
        self.cursor.execute("SELECT * FROM Users WHERE guild_id = ? AND user_id = ?", (player.guild.id, player.id))
        result = self.cursor.fetchone()

        if result is None:
            self.cursor.execute("INSERT INTO Users (guild_id, user_id, EnergyAmount) Values (?, ?, ?)", (player.guild.id, player.id, 0))
            self.connection.commit()

    def UpdateData(self, Data: str, Value, player: discord.Member):
        self.cursor.execute(f"UPDATE Users SET {Data} = ? WHERE guild_id = ? AND user_id = ?", (Value, player.guild.id, player.id))
        self.connection.commit()

    def GetPlayerData(self, player: discord.Member):
        self.cursor.execute("SELECT * FROM Users WHERE guild_id = ? AND user_id = ?", (player.guild.id, player.id))
        result = self.cursor.fetchone()  # Veya fetchall() kullanabilirsiniz

        return result
    
    def SetBasicData(self, player: discord.Member, Register: bool = False):

        print("RESETED")
        if Register:
            self.UpdateData("IsInGame", 1, player=player)
            self.UpdateData("Health", 100, player=player)
            self.UpdateData("Energy", 0, player=player)
            self.UpdateData("ShieldHealth", 25, player=player)
            self.UpdateData("CanSee", 0, player=player)
            self.UpdateData("WaitTour", 0, player=player)
            self.UpdateData("EnergyAmount", 0, player=player)
            self.UpdateData("EnergyBlock", 0, player=player)
            self.UpdateData("ShieldBlock", 0, player=player)
            self.UpdateData("UsedSpell", "NONE", player=player)

        self.UpdateData("IsPlayed", 0, player=player)
        self.UpdateData("MaxHealth", self.MaxHealth, player=player)
        self.UpdateData("MaxShieldHealth", self.MaxShieldHealth, player=player)
        self.UpdateData("MaxEnergy", self.MaxEnergy, player=player)
        self.UpdateData("ExtraDamage", 0, player=player)
        self.UpdateData("IsShieldOn", 0, player=player)

        result = self.GetPlayerData(player=player)
        self.UpdateData("EnergyBlock", result[16]-1 if result[16]-1 > 0 else 0, player=player)
        self.UpdateData("ShieldBlock", result[17]-1 if result[17]-1 > 0 else 0, player=player)

        self.connection.commit()
    
    # BÜYÜ LİSTESİ FONKSİYONLARI

    def GetRandomSingleSpell(self, SpellList:list, removeAddSpeel: bool) -> str:
        spell = random.choice(self.SPEELS)

        while spell in SpellList and (removeAddSpeel and spell == "ADD SPELL"):
            spell = random.choice(self.SPEELS)

        return spell
    
    def GetRandomSpellList(self, Length : int, removeAddSpeel: bool) -> list:
        speelsList = []

        while len(speelsList) < Length - 1:
            a = random.choice(self.SPEELS)

            if a not in speelsList:
                if removeAddSpeel:
                    if a != "ADD SPELL":
                        speelsList.append(a)
                else:
                    speelsList.append(a)

        speelsList.append("NONE")

        #print("RandomSpellList", speelsList)
        return speelsList
    
    def GetSpellList(self, player: discord.Member) -> list:
        SpellList = []

        self.cursor.execute("PRAGMA table_info(Users)")
        columns = self.cursor.fetchall()

        result = self.GetPlayerData(player=player)

        for i in range(self.starterColumnCount, len(columns)):
            SpellList.append(result[i])
        
        #print("SpellList", SpellList)
        return SpellList

    def DefineSpellList(self, Values: list, player: discord.Member):
        for i, value in enumerate(Values):
            #print(i)
            self.UpdateData(f"Spell{i+1}", value, player=player)
    
    def AddSpell(self, player: discord.Member, HowManyTimes: int = 2):
        SpellList = self.GetSpellList(player=player)
        times = 0

        for i in range(len(SpellList)):
            item = SpellList[i]
            if (item == "NONE" or item == "USED" or item == "BLOCKED") and times < HowManyTimes:
                times += 1
                self.UpdateData(f"Spell{i+1}", 
                                self.GetRandomSingleSpell(SpellList, removeAddSpeel=True), 
                                player=player)
                
        # ----

    """def GetRandomSingleSpell(self, SpellList:list, removeAddSpeel: bool) -> list:
        spell = ""

        while True:
            spell = random.choice(self.SPEELS)

            if spell not in SpellList and (removeAddSpeel and spell != "ADD SPELL"): break

        return spell
    
    def GetRandomSpellList(self, Length : int, removeAddSpeel: bool) -> list:
        speelsList = []

        while len(speelsList) < Length - 1:
            a = random.choice(self.SPEELS)

            if a not in speelsList and (removeAddSpeel and a != "ADD SPELL"):
                speelsList.append(a)

        speelsList.append("NONE")

        print("RandonSpellList", speelsList)
        return speelsList"""
    
    """def GetSpellList(self, player:discord.Member) -> list:
        SpellList = []

        self.cursor.execute("PRAGMA table_info(Users)")
        columns = self.cursor.fetchall()

        result = self.GetPlayerData(player=player)

        starterColumnCount = 18

        for i in range(starterColumnCount+1, len(columns)-(starterColumnCount-1)):
            SpellList.append(result[i])
        
        print("SpellList", SpellList)
        return SpellList"""

    """def DefineSpellList(self, Values:list, player: discord.Member):
        SpellListLength = len(self.GetSpellList(player=player))
        
        for i in range(1, SpellListLength+1):
            self.UpdateData(f"Spell{i}", 
                            Values[i-1],
                            player=player)"""
            
    """def AddSpell(self, player=discord.Member, HowManyTimes=2):
        SpellList = self.GetSpellList(player=player)
        times = 0

        for i in range(1, len(SpellList)+1):
            item = SpellList[i-1]
            if (item == "NONE" or item == "USED" or item == "BLOCKED") and times < HowManyTimes:
                times += 1
                self.UpdateData(f"Speel{i}", 
                                self.GetRandomSingleSpell(SpellList, removeAddSpeel=False), 
                                player=player)"""
                
    def BlockSpell(self, player=discord.Member, HowManyTimes=2):
        SpellList = self.GetSpellList(player=player)

        self.UpdateData(f"Spell{random.randint(1, len(SpellList)-1)}",
                        "BLOCKED", 
                        player=player)
        
    def ExchangeSpellList(self, player1=discord.Member, player2=discord.Member):
        player1List = self.GetSpellList(player=player1)
        player2List = self.GetSpellList(player=player2)

        self.DefineSpellList(Values=player1List, player=player2)
        self.DefineSpellList(Values=player2List, player=player1)
    
    def RenewSpellList(self, player=discord.Member):
        SpellListLength = len(self.GetSpellList(player=player))
        
        self.DefineSpellList(Values=self.GetRandomSpellList(Length=SpellListLength,
                                                            removeAddSpeel=False),
                            player=player)     
        
    def RemoveSpellFromList(self, SpellName: str, NewSpellName: str, player: discord.Member):
        for index, value in enumerate(self.GetSpellList(player=player)):
            if value == SpellName:
                self.UpdateData(f"Spell{index+1}", NewSpellName, player=player)
        
    # DISCORD UI

    def ButtonListMaker(self, length:int, names:list, styles:list, emojis:list = None) -> list:
        buttonList = []

        for i in range(length):
            button = Button(label=names[i], emoji=emojis[i] if emojis else None, style=styles[i])
            buttonList.append(button)

        return buttonList

    def ButtonCallbackMatcher(self, buttonList: list, callbackList: list, View:View):
        for i in range(len(buttonList)):
            buttonList[i].callback = callbackList[i]
            View.add_item(buttonList[i])

    def EmbedMaker(self, color, title:str, FieldLengt: int, names:list, values:list, inlines:list, description: str = "") -> Embed:
        embed = Embed(
            title=title,
            color=color,
            description=description
        )

        for i in range(FieldLengt):
            embed.add_field(name=names[i], value=values[i], inline=inlines[i])

        return embed
    
    def ClassicEmbed(self, player: discord.Member, isStarter: bool = False, isLoseOrWin: int = 0, Renewed: int = 0):
        """
        player: Kullanıcı
        isStarter: Eğer ilk defa ClassicEmbed kullanılıyorsa henüz hiçbir eylem yapılmadığından "What Happened?" kaldırılır
        isLoseOrWin: Eğer 0 ise hiçbir galibiyet veya mağlubiyet yoktur. 1 ise mağlubiyettir, 2 ise galibiyettir.
        Renewed: Eğer 0 ise hiçbir galibiyet veya mağlubiyet yoktur. 1 ise rakiptir, 2 ise bizizdir.
        """

        if bool(isLoseOrWin):
            if isLoseOrWin == 1:
                return self.EmbedMaker(color=discord.Colour.red(), title="YOU LOSE!", description="Your Health is 0. So you lose!", FieldLengt=0, names=[], values=[], inlines=[]) 
            elif isLoseOrWin == 2:
                return self.EmbedMaker(color=discord.Colour.green(), title="YOU WON!", description="Your enemy's Health is 0. So you won!", FieldLengt=0, names=[], values=[], inlines=[]) 

        OtherPlayer = self.GetOtherPlayer(player=player)

        result = self.GetPlayerData(player=player)
        result2 = self.GetPlayerData(player=OtherPlayer)

        def GetText(ThePlayer: discord.Member):
            result = self.GetPlayerData(player=ThePlayer)
            a = ""
            for i in self.GetSpellList(player=ThePlayer):
                if i != "USED" and i != "BLOCKED" and i != "NONE":
                    a += f"**{i}**: {Player.FindOut(name=i)[2]}\n"
                    
            b = ""
            b += self.TextDesingerForValues(Name="Health", Value=result[5]) + "\n"
            b += self.TextDesingerForValues(Name="Shield Health", Value=result[9]) + "\n"
            b += self.TextDesingerForValues(Name="Energy", Value=result[7]) + "\n"

            return [a, b]

        a,b = GetText(ThePlayer=player)
        a2,b2 = GetText(ThePlayer=OtherPlayer)
        FieldLenght = 3
        InlineList = [False, True, True, False, True, True]
        Names = ["What Happend?", "YOUR SPELLS", "YOUR STATS", "", "ENEMY'S SPELLS", "ENEMY'S STATS"]

        if Renewed == 1: RenewedText = "- Your spells renewed!"
        elif Renewed == 2: RenewedText = "- Enemy's spells renewed!"
        else: RenewedText = ""

        Values = [f"{Player.FindOut(name=result[18])[3]}\n{Player.FindOut(name=result2[18])[4]}\n{RenewedText}",f"{a}", f"{b}", "", f"{a2}", f"{b2}"]

        if result[13] == 1:
            FieldLenght = 6

        if isStarter:
            return self.EmbedMaker(color=discord.Colour.dark_blue(), title="", FieldLengt=FieldLenght, names=Names[1:], values=Values[1:], inlines=InlineList[1:])

        return self.EmbedMaker(color=discord.Colour.dark_blue(), title="", FieldLengt=FieldLenght, names=Names, values=Values, inlines=InlineList) # Bi embed ayarla
    
    def TextDesingerForValues(self, Name: str, Value: int) -> str:
        return f"```{Name}: {Value}```"

    # HOST

    def HostGame(self):
        ButtonList = self.ButtonListMaker(length=1, names=["Cancel"], emojis=["✖️"], styles=[discord.ButtonStyle.red])

        async def host_callback(interaction: discord.Interaction):
            if self.MainInteraction.user.id == interaction.user.id:
                await interaction.response.send_message(f"Sorry, game Canceled by <@{interaction.user.id}>")
            else:
                await interaction.response.send_message("You're NOT who host this game!", ephemeral=True)

        self.ButtonCallbackMatcher(buttonList=ButtonList, callbackList=[host_callback], View=self)

    def AcceptOrRefuse(self):
        ButtonList = self.ButtonListMaker(length=2, names=["Accept", "Refuse"], emojis=["✔️", "✖️"], styles=[discord.ButtonStyle.success, discord.ButtonStyle.red])

        def Disable():
            for i in self.children:
                i.disabled = True

        async def accept(interaction: discord.Interaction):
            await interaction.response.defer()

            if self.player2.id == interaction.user.id:
                self.SecondInteraction = interaction
                self.CreateData(6, player1=self.player1, player2=self.player2)
                self.RenewSpellList(player=self.player1)
                self.RenewSpellList(player=self.player2)
                Disable()
                
                self.SetBasicData(player=self.player1, Register=True)
                self.SetBasicData(player=self.player2, Register=True)

                player1Embed = self.ClassicEmbed(player=self.MainInteraction.user, isStarter=True)
                player2Embed = self.ClassicEmbed(player=interaction.user, isStarter=True)                  

                await asyncio.gather(
                    interaction.followup.send(
                        view=Game(MainInteraction=self.MainInteraction, player1=self.player1, player2=self.player2, usingFor="Game2"), 
                        embed=player2Embed, 
                        ephemeral=True
                    ),
                    self.MainInteraction.followup.send(
                        view=Game(MainInteraction=self.MainInteraction, player1=self.player1, player2=self.player2, usingFor="Game1"), 
                        embed=player1Embed, 
                        ephemeral=True
                    )
                )
            else:
                await interaction.followup.send("You're NOT invited for this game!", ephemeral=True)

        async def refuse(interaction: discord.Interaction):
            if self.player2.id == interaction.user.id:
                self.SecondInteraction = interaction
                Disable()
                await interaction.response.send_message(f"Sorry, game Canceled by <@{interaction.user.id}>")
            else:
                await interaction.response.send_message("You're NOT invited for this game!", ephemeral=True)

        self.ButtonCallbackMatcher(buttonList=ButtonList, callbackList=[accept, refuse], View=self)

    def SpellListAndGiveThemNewList(self, player: discord.Member) -> int:
        OtherPlayer = self.GetOtherPlayer(player=player)

        def CheckTheListForSpell(player: discord.Member):
            PlayerList = self.GetSpellList(player=player)
            HasSpell: bool = False

            for i in PlayerList:
                if i != "USED" and i != "BLOCKED" and i != "NONE":
                    HasSpell = True

            print("HasSpell", HasSpell)
            return HasSpell
        
        if not CheckTheListForSpell(player=OtherPlayer):
            self.RenewSpellList(player=OtherPlayer)
            return 1

        if not CheckTheListForSpell(player=player):
            self.RenewSpellList(player=player)
            return 2
        
        return 0

    def Game(self, player: discord.Member):
        OtherPlayer = self.GetOtherPlayer(player=player)
        self.UpdateData("IsPlayed", Value=0, player=OtherPlayer)
        self.SetBasicData(player=player)

        result = self.GetPlayerData(player=player)
        result2 = self.GetPlayerData(player=OtherPlayer)

        IsGameRuns = result[2] == 1 and result2[2] == 1

        def ButtonCallbackMatcherForGame(buttonList: list, callbackNameList: list, View:View):
            for i in range(len(buttonList)):
                button = buttonList[i]
                button.callback = CallbackDesigner(button=button, CallbackName=callbackNameList[i])
                View.add_item(buttonList[i])

        def CallbackDesigner(
                            button: Button, 
                            CallbackName: str 
                            ):
            """
            Bunu yapıyorum çünkü Callback'lere parametre yoluyla veri girişi yapmam lazım

            CallbackName:
            Feature --> FeatureCallback()
            Spell --> SpellCallback()
            Exit --> ExitCallback()
            """

            button_label = button.label

            async def FeatureCallback(interaction: discord.Interaction):
                await interaction.response.defer()

                self.FeatureUsed = True

                match button_label:
                    case "Shield":
                        self.UpdateData("IsShieldOn", 1, player=player)
                    case "Extra Damage":
                        self.UpdateData("ExtraDamage", 1, player=player)
                    case "See":
                        if self.GetPlayerData(player=player)[7] < 25: # Eğer enerjisi 25'ten azsa
                            await interaction.followup.send("Sorry! You don't have enough energy for **See**. You wasted the feature. Poor you.", ephemeral=True)
                        else:
                            self.UpdateData("CanSee", 1, player=player)
                    case _: # Diğerleri
                        await interaction.followup.send("Use **/energy (number)** to specify how much energy you will use.", ephemeral=True)

                        self.UpdateData("EnergyAmount", None, player=player)

                        while self.GetPlayerData(player=player)[14] < 10 and self.GetPlayerData(player=player)[15] is None:
                            self.UpdateData("WaitTour", self.GetPlayerData(player=player)[14]+1, player=player)
                            print("Özellik Döngüsünde", self.GetPlayerData(player=player)[15])
                            await asyncio.sleep(2)
                        else:
                            Energy = self.GetPlayerData(player=player)[7]
                            UseEnergy = self.GetPlayerData(player=player)[15]

                            if Energy > UseEnergy: # Eğer var olan enerji miktarı kullanılmak istenen enerji miktarından fazlaysa
                                self.UpdateData("energy", Energy-UseEnergy, player=player) # Kullanılmak istenen miktar var olandan çıkartılır.
                            else: # Değilse
                               self.UpdateData("energy", 0, player=player) # Var olan enerjinin tümünü kullanır

                            if button_label == "Break Shield": self.UpdateData("ShieldHealth", 
                                                                                Player.TakeDamage(MinHealth=0, Health=self.GetPlayerData(player=OtherPlayer)[9], Damage=Energy), 
                                                                                player=OtherPlayer)
                                    
                            elif button_label == "Repair Shield": self.UpdateData("ShieldHealth", 
                                                                                    Player.Heal(MaxHealth=self.MaxShieldHealth, Health=self.GetPlayerData(player=player)[9], Heal=Energy), 
                                                                                    player=player)

            async def SpellCallback(interaction: discord.Interaction):
                await interaction.response.defer()

                if IsGameRuns:
                    print(player.id, "played")
                    self.UpdateData("UsedSpell", button.label, player=player) # Kullanılan yeteneği ayarla

                    sayed = False

                    for i in self.children[6:12]: # Diğer özellikler arası dolanır
                        if not i.disabled and not sayed: # Eğer diğer özellikleri kullanabiliyorsa kullanması için uyarır
                            sayed = True
                            await interaction.followup.send("Don't forget to use a feature (blue ones)", ephemeral=True) # Kullanıcıyı bir özellik seçme konusunda uyar

                    while self.GetPlayerData(player=player)[3] == 0 or self.GetPlayerData(player=OtherPlayer)[3] == 0:
                        print("DÖNGÜDE", self.GetPlayerData(player=player)[3], self.GetPlayerData(player=OtherPlayer)[3])
                        self.UpdateData("IsPlayed", Value=1, player=player)
                        await asyncio.sleep(1)
                    else:
                        self.UpdateData("IsPlayed", Value=1, player=player)
                        self.UpdateData("IsPlayed", Value=1, player=OtherPlayer)

                    self.RemoveSpellFromList(SpellName=button.label, NewSpellName="USED", player=player) # Yeteneği kaldır
                    self.UseSpell(SpellName=button.label, player=player) # Yeteneği kullandır
                        
                    if self.player1.id == player.id: user = "1"
                    elif self.player2.id == player.id: user = "2"

                    await asyncio.sleep(3)
                    
                    print("ÇALIŞTIĞINI SANMIYORUM")

                    result = self.GetPlayerData(player=player)
                    result2 = self.GetPlayerData(player=OtherPlayer)

                    isLoseOrWin = 0

                    if result[5] <= 0:
                        isLoseOrWin = 1       
                        usingFor = "End"
                        self.exit(player=player)
                        print("ÇALIŞTIĞINI SANMIYORUM 1")
                    elif result2[5] <= 0:
                        isLoseOrWin = 2
                        usingFor = "End"
                        self.exit(player=player)
                        print("ÇALIŞTIĞINI SANMIYORUM 2")

                    Renewed = self.SpellListAndGiveThemNewList(player=player)

                    classicEmbed = self.ClassicEmbed(player=player,
                                                    isLoseOrWin=isLoseOrWin,
                                                    Renewed=Renewed
                                                    )

                    await interaction.followup.send(embed=classicEmbed,
                                                    view=Game(MainInteraction=self.MainInteraction, player1=self.player1, player2=self.player2, usingFor=f"Game{user}", OldGameObject=self),
                                                    ephemeral=True, 
                                                    files=Player.GetGIF(SpellName1=result[18],SpellName2=result2[18], Gun=result2[10], player=user))
                else:
                    await interaction.followup.send("Sorry Pal game is over.", ephemeral=True)

            async def ExitCallback(interaction: discord.Interaction):
                await interaction.response.defer()

                if player.id == interaction.user.id:
                    self.exit(player=player)
                    await interaction.followup.send(f"<@{self.player1.id}> and <@{self.player2.id}>'s game is over. <@{player.id}> wanted to quit.")
                else:
                    await interaction.followup.send("You're NOT invited for this game!", ephemeral=True)
            
            match CallbackName:
                case "Feature":
                    return FeatureCallback
                case "Spell":
                    return SpellCallback
                case "Exit":
                    return ExitCallback

        if IsGameRuns:
            names = []
            emojis = []
            styles = []
            SpellList = self.GetSpellList(player=player)

            self.GetPlayerData(player=OtherPlayer)
            self.GetPlayerData(player=player)
            callbackNameList = []

            for i in range(len(SpellList)):
                names.append(SpellList[i])
                emojis.append(Player.FindOut(SpellList[i])[0])
                styles.append(Player.FindOut(SpellList[i])[1])
                callbackNameList.append("Spell")

            names.append("Shield"); emojis.append("🛡️"), styles.append(discord.ButtonStyle.blurple); callbackNameList.append("Feature")
            names.append("Break Shield"); emojis.append("🤜"), styles.append(discord.ButtonStyle.blurple); callbackNameList.append("Feature")
            names.append("Repair Shield"); emojis.append("🔨"), styles.append(discord.ButtonStyle.blurple); callbackNameList.append("Feature")
            names.append("Extra Damage"); emojis.append("🗡️"), styles.append(discord.ButtonStyle.blurple); callbackNameList.append("Feature")
            names.append("See"); emojis.append("👀"), styles.append(discord.ButtonStyle.blurple); callbackNameList.append("Feature")
            names.append("Exit"); emojis.append("👀"), styles.append(discord.ButtonStyle.red); callbackNameList.append("Exit")

            ButtonList = self.ButtonListMaker(length=12, names=names, emojis=emojis, styles=styles)      

            ButtonCallbackMatcherForGame(buttonList=ButtonList, callbackNameList=callbackNameList, View=self)

            for i in self.children:
                if i.label == "USED" or i.label == "BLOCKED" or i.label == "NONE":
                    i.disabled = True

            if result[16] != 0:
                for i in self.children[self.SpellListLength:len(self.children)-2]:
                    i.disabled = True

            if result[17] != 0: 
                self.children[self.SpellListLength].disabled = True
            
    # BÜYÜLER

    def GetOtherPlayer(self, player: discord.Member):
        playerList = [self.player1, self.player2]
        for i in playerList:
            if i == player: playerList.remove(i)

        OtherPlayer = playerList[0]

        return OtherPlayer

    def TakeDamage(self, Damage: int, player: discord.Member, TakeEnergy: bool = True):
        """
        Eğer ekstra hasar açıksa hasar arttırılmalı
        Eğer kalkan açıksa kalkanı canı kadar hasar bloklanmalı

        Öncelik sırası: ekstra, kalkan
        """
        OtherPlayer = self.GetOtherPlayer(player=player)
        result = self.GetPlayerData(player=player)
        result2 = self.GetPlayerData(player=OtherPlayer)

        if result2[12] == 1:
            Damage = Damage * 140 / 100 # Hasarın 140%'ını alır

        if result[10] == 1:
            Damage -= Damage * result[9] / self.MaxShieldHealth
            # Kalkan canına göre hasar bloklanır. Mesela eğer hasar 20, kalkan canı 25 ve kalkanın maksimum canı 100 ise
            # 20 / 25 * 100 = 5
            # Bu sonuç hasarın tümünden çıkarılır
            # 20 - 5 = 15
            # Hasar can yüzdesi kadar bloklanmış oldu.

        Damage = round(Damage) # Hasarın yüzdelikli bir değer olmasını engeller

        Health = result[5] - Damage # Can - Hasar

        if Health < 0:
            Health = 0
        
        self.UpdateData("Health", Health, player=player)

        print("Damage", Damage)

        if TakeEnergy:
            self.TakeEnergy(ExtraEnergy=Damage, player=OtherPlayer)

    # Küçük çaplı useSpell()
    def Heal(self, Heal: int, player: discord.Member):
        result = self.GetPlayerData(player=player) 

        Health = result[5] + Heal # Can + iyileştirme

        if Health > self.MaxHealth:
            Health = self.MaxHealth

        self.UpdateData("Health", Health, player=player)

    def TakeEnergyDamage(self, Damage: int, player: discord.Member):
        result = self.GetPlayerData(player=player) 

        Energy = result[7] - Damage # Enerji - Hasar

        if Energy < 0:
            Energy = 0

        self.UpdateData("Energy", Energy, player=player)

    def TakeEnergy(self, ExtraEnergy: int, player: discord.Member):
        result = self.GetPlayerData(player=player) 

        Energy = result[7] + ExtraEnergy # Enerji + Ekstra Enerji

        if Energy > self.MaxEnergy:
            Energy = self.MaxEnergy

        self.UpdateData("Energy", Energy, player=player)

    def Gun(self, Damage: int, player: discord.Member):
        result = self.GetPlayerData(player=player)
        OtherPlayer = self.GetOtherPlayer(player=player)

        Health = result[5] - Damage
        EnemyEnergy = self.GetPlayerData(player=OtherPlayer)[7] + Damage

        if result[10] == 1: # Eğer kalkanı açıksa
            self.UpdateData("Health", Health, player=OtherPlayer) # Hasarı diğerine verir
            self.UpdateData("Energy", EnemyEnergy, player=player)
        else: # Değilse
            self.UpdateData("Health", Health, player=player) # Hasarı kendisine verir
            self.UpdateData("Energy", EnemyEnergy, player=OtherPlayer)

    def EnergyBlock(self, player: discord.Member):
        self.UpdateData("EnergyBlock", 3, player=player)

    def ShieldBlock(self, player: discord.Member):
        self.UpdateData("ShieldBlock", 3, player=player)

    def UseSpell(self, SpellName: str, player: discord.Member):
        OtherPlayer = self.GetOtherPlayer(player=player)

        match SpellName:
            case "LIGHTNING": 
                self.TakeDamage(20, player=OtherPlayer)
                self.TakeEnergyDamage(10, player=OtherPlayer)
            case "MAGIC TORNADO": 
                self.TakeDamage(30, player=OtherPlayer)
                self.TakeEnergyDamage(20, player=OtherPlayer)
            case "PIT": 
                self.TakeDamage(20, player=OtherPlayer)
                self.TakeEnergyDamage(10, player=OtherPlayer)
            case "HEAL": 
                self.Heal(30, player=player)
            case "ULTRA HEAL": 
                self.Heal(100, player=player)
                self.Heal(100, player=OtherPlayer)
            case "THROW BOOK": 
                self.TakeDamage(15, player=OtherPlayer)
                self.TakeEnergyDamage(5, player=OtherPlayer)
            case "ENERGY RESET": 
                self.TakeEnergyDamage(100, player=player)
                self.TakeEnergyDamage(100, player=OtherPlayer)
            case "GUN": 
                self.Gun(Damage=50, player=OtherPlayer)
            case "STAR": 
                self.TakeDamage(20, player=OtherPlayer)
                self.TakeEnergyDamage(30, player=OtherPlayer)
            case "TRAIN": # Tren gelir hoş gelir
                self.TakeDamage(40, player=OtherPlayer, TakeEnergy=False)
                self.TakeEnergyDamage(10, player=OtherPlayer)

                self.TakeDamage(40, player=player, TakeEnergy=False)
                self.TakeEnergyDamage(10, player=player)
            case "TREE": 
                self.TakeDamage(20, player=OtherPlayer)
                self.TakeEnergyDamage(10, player=OtherPlayer)
            case "TORNADO": 
                self.TakeDamage(20, player=OtherPlayer)
                self.TakeEnergyDamage(20, player=OtherPlayer)
            case "BLOCK SPELL": 
                self.BlockSpell(player=OtherPlayer)
            case "TAKE ENERGY":
                self.TakeEnergy(ExtraEnergy=30, player=player)
            case "BLOCK SHIELD": 
                self.ShieldBlock(player=OtherPlayer)
            case "ADD SPELL": 
                self.AddSpell(player=player)
            case "EXCHANGE": 
                self.ExchangeSpellList(player1=player, player2=OtherPlayer) # Sıralamanın pek de bir önemi yok sonuçta değişiyorlar
            case "ENERGY BLOCKER": 
                self.EnergyBlock(player=OtherPlayer)
            case _:
                print("DIDN'T WORK!")

    # Diğer şeyler

    def exit(self, player: discord.Member):
        OtherPlayer = self.GetOtherPlayer(player=player)
        self.UpdateData("isInGame", 0, player=player)
        self.UpdateData("isInGame", 0, player=OtherPlayer)