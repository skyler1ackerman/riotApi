import pickle, jsons, pprint
from dataclasses import dataclass, field
from typing import List

pp = pprint.PrettyPrinter(indent=4)

@dataclass
class Player:
    platformId: str = None
    accountId: str = None
    summonerName: str = None
    summonerId: str = None
    currentPlatformId: str = None
    currentAccountId: str = None
    matchHistoryUri: str = None
    profileIcon: int = None

    def __str__(self):
        return self.summonerName

@dataclass
class ParticipantId:
    participantId: int
    player: Player

@dataclass
class Timeline:
    participantId: int
    role: str
    lane: str
    creepsPerMinDeltas: dict = field(default_factory=dict)
    xpPerMinDeltas: dict = field(default_factory=dict)
    goldPerMinDeltas: dict = field(default_factory=dict)
    csDiffPerMinDeltas: dict = field(default_factory=dict)
    xpDiffPerMinDeltas: dict = field(default_factory=dict)
    damageTakenPerMinDeltas: dict = field(default_factory=dict)
    damageTakenDiffPerMinDeltas: dict = field(default_factory=dict)
    
@dataclass
class Stats:
    participantId: int = None
    win: bool = None
    item0: int = None
    item1: int = None
    item2: int = None
    item3: int = None
    item4: int = None
    item5: int = None
    item6: int = None
    kills: int = 0
    deaths: int = 0
    assists: int = 0
    largestKillingSpree: int = 0
    largestMultiKill: int = 0
    killingSprees: int = 0
    longestTimeSpentLiving: int = 0
    doubleKills: int = 0
    tripleKills: int = 0
    quadraKills: int = 0
    pentaKills: int = 0
    unrealKills: int = 0
    totalDamageDealt: int = 0
    magicDamageDealt: int = 0
    physicalDamageDealt: int = 0
    trueDamageDealt: int = 0
    largestCriticalStrike: int = 0
    totalDamageDealtToChampions: int = 0
    magicDamageDealtToChampions: int = 0
    physicalDamageDealtToChampions: int = 0
    trueDamageDealtToChampions: int = 0
    totalHeal: int = 0
    totalUnitsHealed: int = 0
    damageSelfMitigated: int = 0
    damageDealtToObjectives: int = 0
    damageDealtToTurrets: int = 0
    visionScore: int = 0
    timeCCingOthers: int = 0
    totalDamageTaken: int = 0
    magicalDamageTaken: int = 0
    physicalDamageTaken: int = 0
    trueDamageTaken: int = 0
    goldEarned: int = 0
    goldSpent: int = 0
    turretKills: int = 0
    inhibitorKills: int = 0
    totalMinionsKilled: int = 0
    neutralMinionsKilled: int = 0
    neutralMinionsKilledEnemyJungle: int = 0
    totalTimeCrowdControlDealt: int = 0
    champLevel: int = 0
    visionWardsBoughtInGame: int = 0
    sightWardsBoughtInGame: int = 0
    wardsPlaced: int = 0
    wardsKilled: int = 0
    combatPlayerScore: int = 0
    objectivePlayerScore: int = 0
    totalPlayerScore: int = 0
    totalScoreRank: int = 0
    playerScore0: int = 0
    playerScore1: int = 0
    playerScore2: int = 0
    playerScore3: int = 0
    playerScore4: int = 0
    playerScore5: int = 0
    playerScore6: int = 0
    playerScore7: int = 0
    playerScore8: int = 0
    playerScore9: int = 0
    perk0: int = None
    perk0Var1: int = None
    perk0Var2: int = None
    perk0Var3: int = None
    perk1: int = None
    perk1Var1: int = None
    perk1Var2: int = None
    perk1Var3: int = None
    perk2: int = None
    perk2Var1: int = None
    perk2Var2: int = None
    perk2Var3: int = None
    perk3: int = None
    perk3Var1: int = None
    perk3Var2: int = None
    perk3Var3: int = None
    perk4: int = None
    perk4Var1: int = None
    perk4Var2: int = None
    perk4Var3: int = None
    perk5: int = None
    perk5Var1: int = None
    perk5Var2: int = None
    perk5Var3: int = None
    perkPrimaryStyle: int = None
    perkSubStyle: int = None
    statPerk0: int = None
    statPerk1: int = None
    statPerk2: int = None
    neutralMinionsKilledTeamJungle: int = None
    firstInhibitorKill: bool = None
    firstInhibitorAssist: bool = None
    firstBloodKill: bool = None
    firstBloodAssist: bool = None
    firstTowerKill: bool = None
    firstTowerAssist: bool = None

@dataclass
class Participant:
    participantId: int
    teamId: int
    championId: int
    spell1Id: int
    spell2Id: int
    stats: Stats
    timeline: Timeline

@dataclass
class Ban:
    championId: int
    pickTurn: int
    
@dataclass
class Team:
    teamId: int
    win: bool
    firstBlood: bool
    firstTower: bool
    firstBaron: bool
    firstDragon: bool
    firstRiftHerald: bool
    towerKills: int
    inhibitorKills: int
    baronKills: int
    dragonKills: int
    vilemawKills: int
    riftHeraldKills: int
    dominionVictoryScore: int
    bans: List[Ban]
    firstInhibitor: bool = None

@dataclass
class Match:
    gameId: int
    platformId: str
    gameCreation: int
    gameDuration: int
    queueId: int
    mapId: int
    seasonId: int
    gameVersion: str
    gameMode: str
    gameType: str
    teams: List[Team]
    participants: List[Participant]
    participantIdentities: List[ParticipantId]
    userIndex: int = None

    def get_id(self, sum_id):
        for part in self.participantIdentities:
            if sum_id == part.player.accountId:
                self.userIndex = part.participantId-1

@dataclass
class MatchList:
    matchlist: List[Match]

    def __len__(self):
        return len(self.matchlist)
# %%
