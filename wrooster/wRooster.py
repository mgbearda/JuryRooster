from xml.dom.minidom import parse, parseString
from datetime import datetime, timedelta
import time
import re
import math
import random
import copy
import sys

onmogelijkScore = 60*20 # 20 uur

# todos
# * aanvangtijd anders voor spelers dan jury
# * genereer ook team pagina's
# * genereer speler cariere pagina
# * genereer speler agenda / ical
# * wedstrijd resultaten
# * wedstrijd eigenschap
# * code opsplitsen in;
#   - weekelijks nieuwe resultaten binnen halen
#   - eenmalig jury rooster generen
#   - spelers pagina genereren

reisminuten = { 'zuidlaren-aqualaren' : 0,
                'sneek-it rak' : 90,
                'groningen-de parrel' : 60,
                'heerenveen-sportstad heerenveen' : 75,
                'heerenveen-sportstad heerenveen bv' : 75,
                'delfzijl-dubbelslag' : 75,
                'drachten-de welle' : 75,
                'stadskanaal-zwembad pagecentrum' : 75,
                'stadskanaal-sportfondsenbad stadskanaal' : 75,
                'zwolle-aabad' : 90,
                'zwolle-bad bloemendal' : 90,
                'leeuwarden-de blauwe golf' : 105,
                'meppel-bad hesselingen' : 90,
                'beilen-de peppel' : 60,
                'assen-de bonte wever - assen' : 60,
                'assen-de bonte wever' : 60,
                'smilde-de smelte' : 75,
                'veendam-tropiqua zwemparadijs' : 60,
                'coevorden-de swaneburg' : 105,
                'coevorden-sportcomplex de zwanenburg' : 105,
                'groningen-helperbad' : 45,
                'joure-zb de stiennen flier' : 90,
                'joure-de stiennen flier' : 90,
                'bergum-wetterstins' : 90,
                'burgum-de wetterstins' : 90,
                'winschoten-de watertoren' : 75,
                'hoogezand-kalkwijck' : 45,
                'hoogezand-de kalkwijck' : 45,
                'stiens-it gryn' : 120,
                'franeker-bloemketerp' : 120,
                'bolsward-vitalo sportfondsenbad' : 105,
                'bolsward-optisport vitaloo' : 105,
                'bolsward-vitaloo' : 105,
                'hoogeveen-de dolfijn' : 75,
                'emmen-aquarena' : 75,
                'dokkum-tolhuisbad' : 105,
                'rijssen-de koerbelt' : 135,
                'neede-t spilbroek' : 150
              }
wedstrijdLengte = { 'N-DG1B': 25,
                    'N-BG1B': 45,
                    'N-D3A': 45,
                    'N-H4A': 45,
                    'N-H3A': 45,
                    'N-H2A': 45,
                    'N-H1A': 60,
                    'B-HRC' : 60
                  }
juryBenodigd = {    'N-DG1B': 2,
                    'N-BG1B': 3,
                    'N-D3A': 3,
                    'N-H4A': 3,
                    'N-H3A': 3,
                    'N-H2A': 3,
                    'N-H1A': 3,
                    'B-HRC' : 3
                  }

def latin1_to_ascii (unitxt):
    xlate={0xc0:'A', 0xc1:'A', 0xc2:'A', 0xc3:'A', 0xc4:'A', 0xc5:'A', 0xc6:'Ae', 0xc7:'C', 0xc8:'E', 0xc9:'E', 0xca:'E', 0xcb:'E', 0xcc:'I', 0xcd:'I', 0xce:'I', 0xcf:'I', 0xd0:'Th', 0xd1:'N', 0xd2:'O', 0xd3:'O', 0xd4:'O', 0xd5:'O', 0xd6:'O', 0xd8:'O', 0xd9:'U', 0xda:'U', 0xdb:'U', 0xdc:'U', 0xdd:'Y', 0xde:'th', 0xdf:'ss', 0xe0:'a', 0xe1:'a', 0xe2:'a', 0xe3:'a', 0xe4:'a', 0xe5:'a', 0xe6:'ae', 0xe7:'c', 0xe8:'e', 0xe9:'e', 0xea:'e', 0xeb:'e', 0xec:'i', 0xed:'i', 0xee:'i', 0xef:'i', 0xf0:'th', 0xf1:'n', 0xf2:'o', 0xf3:'o', 0xf4:'o', 0xf5:'o', 0xf6:'o', 0xf8:'o', 0xf9:'u', 0xfa:'u', 0xfb:'u', 0xfc:'u', 0xfd:'y', 0xfe:'th', 0xff:'y', 0xa1:'!', 0xa2:'{cent}', 0xa3:'{pound}', 0xa4:'{currency}', 0xa5:'{yen}', 0xa6:'|', 0xa7:'{section}', 0xa8:'{umlaut}', 0xa9:'{C}', 0xaa:'{^a}', 0xab:'<<', 0xac:'{not}', 0xad:'-', 0xae:'{R}', 0xaf:'_', 0xb0:'{degrees}', 0xb1:'{+/-}', 0xb2:'{^2}', 0xb3:'{^3}', 0xb4:"'", 0xb5:'{micro}', 0xb6:'{paragraph}', 0xb7:'*', 0xb8:'{cedilla}', 0xb9:'{^1}', 0xba:'{^o}', 0xbb:'>>', 0xbc:'{1/4}', 0xbd:'{1/2}', 0xbe:'{3/4}', 0xbf:'?', 0xd7:'*', 0xf7:'/' }
    txt = ''
    for c in unitxt:
        if xlate.has_key(ord(c)):
            txt += xlate[ord(c)]
        elif ord(c) >= 0x80:
            pass
        else:
            txt += c
    return txt

def parseDateI(txt): #2011-12-31
    return datetime.datetime.strptime(txt, "%Y-%m-%d")
def parseDate(txt): #31-12-2011
    return datetime.strptime(txt, "%d-%m-%Y")
def parseDateTime(txt): #22-10-11 17:30 or 10-22-2011 17:30
    styles = ["%d-%m-%y %H:%M", "%m-%d-%Y %H:%M"]
    for style in styles:
        try:
            d = datetime.strptime(txt, style)
            return d
        except:
            pass
    return datetime.now()
def time2str(t):
    t2 = t
    if t2.second > 30:
        t2 = t2 + timedelta(0,60-t2.second)
    return t2.strftime("%d/%m/%y %H:%M")
def date2str(t):
    t2 = t
    if t2.second > 30:
        t2 = t2 + timedelta(0,60-t2.second)
    return t2.strftime("%d/%m/%y")

class Team:
    def __init__(self, naam, alias):
        self.naam = naam
        self.alias = alias
        self.minutenVoorbespreken = 0
        self.minutenNabespreken = 0

class Wedstrijd:
    def __init__(self, aanvang, thuis, uit, locatie, afd, matchId, thuisBad):
        global wedstrijdLengte
        self.aanvang = aanvang
        self.duur = wedstrijdLengte[afd]
        self.matchId = matchId
        self.afgelopen = aanvang + timedelta(0, self.duur*60-1)
        self.thuis = thuis
        self.uit = uit
        self.parseLocatie(locatie)
        if self.locatieCode == thuisBad:
            self.vertrek = self.aanvang# - timedelta(0, 15*60-1) # kwartier voor wedstrijd rust
            self.thuisKomst = self.afgelopen
        else:
            self.vertrek = self.aanvang - self.reistijd
            self.thuisKomst = self.afgelopen + self.reistijd
        global juryBenodigd
        self.juryNodig = juryBenodigd[afd]
        self.spelerStartTijd = self.vertrek
        self.spelerEindTijd = self.thuisKomst
        self.juryStartTijd = self.aanvang
        self.juryEindTijd = self.afgelopen
    def parseLocatie(self, loc):
        loc = loc.replace("'", "")
        loc = loc.replace("`", "")
        m = re.match('([\w\s-]+)\(([\w\s]+)\)', loc)
        zwemb = m.group(1).strip().lower()
        plaats = m.group(2).strip().lower()
        self.locatieCode = '%s-%s' % (plaats, zwemb)
        global reisminuten
        self.reistijd = timedelta(0, reisminuten[self.locatieCode]*60)

class Speler:
    def __init__(self, naam, heeftWsinds):
        self.naam = naam
        self.heeftWsinds = heeftWsinds
        self.heeftWtot = datetime(2020,1,1,0,0)
        self.teams = []
        self.bezigMetWedstrijden = []
        self.thuisWedstrijden = []
        self.reistijdNaarThuisWedstrijd = 10
        self.jurerenBij = []
        self.score = 0
        self.diffWithMeanScore = 0
    def addTeam(self, team, startDatum, eindDatum, capNr, role):
        self.teams.append((team, startDatum, eindDatum, capNr, role))
    def verwerkWedstrijdRooster(self, wedstrijden, thuisBad):
        for w in wedstrijden:
            for (t, startDatum, eindDatum, capNr, role) in self.teams:
                if (w.thuis == t and w.aanvang > startDatum and w.aanvang < eindDatum) or (w.uit == t and w.aanvang > startDatum and w.aanvang < eindDatum):
                    self.bezigMetWedstrijden.append((w, w.spelerStartTijd - timedelta(0, t.minutenVoorbespreken*60), w.spelerEindTijd + timedelta(0, t.minutenNabespreken*60)))
                    if (w.locatieCode == thuisBad):
                        self.thuisWedstrijden.append((w, w.spelerStartTijd, w.spelerEindTijd))
        # sorteer wedstrijden
        self.bezigMetWedstrijden = sorted(self.bezigMetWedstrijden, key=lambda w: w[1])
        self.thuisWedstrijden = sorted(self.thuisWedstrijden, key=lambda w: w[1])
    def calculateMyScore(self, state):
        wedstrOmogelijk = []
        # controleer niet dubbel jureren & vul jurerenBij-lijst
        self.jurerenBij = []
        for (wedstr, jury) in state.juryVoorWedstrijd.iteritems():
            maalDezeJury = 0
            for persoon in jury:
                if persoon == self:
                    maalDezeJury += 1
            if maalDezeJury > 0:
               self.jurerenBij.append(wedstr)
            if maalDezeJury > 1:
                wedstrOmogelijk.append(wedstr)
        for wJureren in self.jurerenBij:
            if (wJureren.aanvang < self.heeftWsinds) or (wJureren.aanvang > self.heeftWtot):
                wedstrOmogelijk.append(wJureren) # heeft nog geen W
            if self.speelWedstrijd(wJureren.juryStartTijd, wJureren.juryEindTijd):
                wedstrOmogelijk.append(wJureren) # kan niet jureren als speler al zelf een wedstrijd speelt
        # maak roosters
        zonderJureren = self.thuisWedstrijden
        Jureren = [(w, w.juryStartTijd, w.juryEindTijd) for w in self.jurerenBij]
        metJureren = zonderJureren[:]
        metJureren.extend(Jureren)
        # bereken tijd kwijt aan thuiswedstrijden
        self.score = (self.tijdKwijtAanRooster(metJureren) - self.tijdKwijtAanRooster(zonderJureren))
        global onmogelijkScore
        onmogelijkSet = set(wedstrOmogelijk)
        self.score += len(onmogelijkSet) * onmogelijkScore
        return self.score, onmogelijkSet
    def tijdKwijtAanRooster(self,rooster):
        # sorteer rooster
        rooster = sorted(rooster, key=lambda w: w[1])
        tijdBenodigd = 0
        prvEnd = datetime(2000,1,1,0,0)
        for w,curStart,curEnd in rooster:
            tijdTussenWedstrijden = (curStart-prvEnd).seconds/60 # in minuten
            if tijdTussenWedstrijden > 2 * self.reistijdNaarThuisWedstrijd:
                tijdBenodigd += 2*self.reistijdNaarThuisWedstrijd # in minuten
            else :
                tijdBenodigd += tijdTussenWedstrijden
            tijdBenodigd += w.duur # in minuten
            prvEnd = curEnd
        return tijdBenodigd
    def speelWedstrijd(self, testStart, testEind):
        for (w, aStrart, sEind) in self.bezigMetWedstrijden:
            if aStrart < testEind and testStart < sEind:
                return True
        return False
    def printWedstrijdRooster(self):
        print "vertrek:       start:         wedstrijd:"
        for (w, aS, aE) in self.bezigMetWedstrijden:
            print "%s %s %s - %s" % ( time2str(aS), time2str(w.aanvang), w.thuis.naam, w.uit.naam)
    def printJuryRooster(self):
        print "start:         wedstrijd:"
        for w in self.jurerenBij:
            print "%s %s %s - %s" % ( time2str(w.aanvang), w.thuis.naam, w.uit.naam)

class State:
    def __init__(self, spelersMetW):
        self.score = sys.maxint
        self.keerOnmogelijk = 0
        self.onmogelijk = []
        self.fixedJury = []
        self.juryVoorWedstrijd = {}
        self.wCount= {}
        for sw in spelersMetW:
            self.wCount[sw] = 0
        self.totaalJuryNodig = 0
        self.maxKeerWen = 0
    def FixJury(self, speler, wedstrLst):
        for wedstr in wedstrLst:
            self.fixedJury.append((wedstr, speler))
    def clone(self, spelersMetW):
        s = State(spelersMetW)
        s.score = self.score
        s.keerOnmogelijk = self.keerOnmogelijk
        for (speler, wedstr) in self.onmogelijk:
            s.onmogelijk.append((speler, wedstr))
        for w, jury in self.juryVoorWedstrijd.iteritems():
            s.juryVoorWedstrijd[w] = jury[:]
        for sp, cnt in self.wCount.iteritems():
            s.wCount[sp] = cnt
        s.totaalJuryNodig = self.totaalJuryNodig
        s.maxKeerWen = self.maxKeerWen
        for (wedstr, speler) in self.fixedJury:
            s.fixedJury.append((wedstr, speler))
        return s

    def randomInit(self, thuisWedstrijden, spelers, spelersMetW, app):
        self.totaalJuryNodig = 0
        for w in thuisWedstrijden:
            self.totaalJuryNodig += w.juryNodig
        nSpelersMetW = len(spelersMetW)
        self.maxKeerWen = int(math.ceil(float(self.totaalJuryNodig)/float(nSpelersMetW)))+3
        juryPlaatsenGevuld = 0;
        for w in thuisWedstrijden:
            self.juryVoorWedstrijd[w] = []
        for (wedstr, speler) in self.fixedJury:
            self.juryVoorWedstrijd[wedstr].append(speler)
        for w in thuisWedstrijden:
            numJuryNogNodig = w.juryNodig - len(self.juryVoorWedstrijd[w])
            for i in range(numJuryNogNodig):
                wer = self.getFreeRandomWer(w.juryStartTijd, w.juryEindTijd, app)
                self.juryVoorWedstrijd[w].append(wer)
                self.wCount[wer] += 1
                juryPlaatsenGevuld += 1

    def calculateScore(self, spelersMetW):
        self.score = 0
        self.keerOnmogelijk = 0
        self.onmogelijk = []
        scoreSum = 0
        for s in spelersMetW:
            sc, onm = s.calculateMyScore(self)
            for w in onm:
                self.onmogelijk.append((s, w))
            scoreSum += sc
            self.keerOnmogelijk += len(onm)
        meanScore = scoreSum/len(spelersMetW)
        for s in spelersMetW:
            s.diffWithMeanScore = meanScore - s.score
            #if s.diffWithMeanScore > 0:
            #    self.score += s.diffWithMeanScore
            self.score += math.fabs(s.diffWithMeanScore)

    def getRandomWer(self, juryPlaatsenGevuld, spelersMetW):
        # geef random w'er terug met grotere kans als nog weinig keren ingeroosterd is
        maxCounts = len(spelersMetW) * self.maxKeerWen
        idx = random.randint(0, maxCounts-juryPlaatsenGevuld-1)
        for wer, keer in self.wCount.iteritems():
            if idx <= (self.maxKeerWen-keer):
                return wer
            idx -= (self.maxKeerWen-keer)
        return None
    def getFreeRandomWer(self, start, end, app):
        global onmogelijkScore
        possibleWers = app.getWersAtDate(start)
        maxScore = 0
        totalScore = 0
        for w in possibleWers:
            maxScore = max(w.score, maxScore)
            totalScore += w.score
        maxTries = 100
        desiredScore = int(maxScore*1.1+1)
        for tryId in range(maxTries):
            maxRnd = desiredScore * len(possibleWers) - totalScore
            idx = random.randint(1, maxRnd)
            for wer in possibleWers:
                scoreRemaining = desiredScore-w.score
                if idx <= scoreRemaining:
                    if not wer.speelWedstrijd(start, end):
                        return wer # geef alleen speler terug die niet al een wedstrijd aan het spelen is
                    else:
                        if (tryId == maxTries-1):
                            return wer # er kan niemand gevonden worden, geef dan toch maar iemand terug
                        else:
                            break # try new
                idx -= scoreRemaining
    def getWerHighScoreHighProb(self, eindDatum, app):
        allWers = app.getWersAtDate(eindDatum)
        totalScore = 0
        for wer in allWers:
            totalScore += wer.score
        randValue = random.randint(0, totalScore)
        for wer in allWers:
            if (randValue < wer.score):
                return wer
            randValue -= wer.score
    def getWerLowScoreHighProb(self, datum, app):
        allWers = app.getWersAtDate(datum)
        maxScore = 0
        totalScore = 0
        for wer in allWers:
            maxScore = max(maxScore, wer.score)
            totalScore += wer.score
        randValue = random.randint(0, len(allWers)*maxScore-totalScore)
        for wer in allWers:
            if (randValue < maxScore - wer.score):
                return wer
            randValue -= maxScore - wer.score
    def shuffle2Wers(self, eindDatum, app):
        # pick random jury plaats
        if self.keerOnmogelijk > 0:
            randIdx1 = random.randint(0, self.keerOnmogelijk-1)
            werOut, w = self.onmogelijk[randIdx1]
            for (wedstr, speler) in self.fixedJury:
                if (wedstr == w and werOut == speler):
                    print "FAILED! Probeer fixed jury te verwijderen : %s " % werOut.naam
                    return
            werIn = self.getFreeRandomWer(w.juryStartTijd, w.juryEindTijd, app)

            print "%d: %s vervangt %s" % (randIdx1, werIn.naam, werOut.naam)

            # update w'er
            werOutIdx = 0
            for wer in self.juryVoorWedstrijd[w]:
                if wer==werOut:
                    break
                else:
                    werOutIdx += 1
            self.juryVoorWedstrijd[w][werOutIdx] = werIn
            # update administratie
            self.wCount[werOut] -= 1
            self.wCount[werIn] += 1
        else:
            werOut = self.getWerHighScoreHighProb(eindDatum, app)
            if (werOut == None):
                return
            w = werOut.jurerenBij[random.randint(0,len(werOut.jurerenBij)-1)]
            werIn = self.getWerLowScoreHighProb(w.aanvang, app)
            if (werIn == None):
                return
            for (wedstr, speler) in self.fixedJury:
                if (wedstr == w and werOut == speler):
                    print "Probeer fixed w'er aan te passen : %s " % werOut.naam
                    return
            print "%s vervangt %s" % (werIn.naam, werOut.naam)
            # find werIdx
            werOutIdx = 0
            for wer in self.juryVoorWedstrijd[w]:
                if wer == werOut:
                    break
                werOutIdx += 1
            if werOutIdx >= len(self.juryVoorWedstrijd[w]):
                return
            # update w'er
            self.juryVoorWedstrijd[w][werOutIdx] = werIn
            # update administratie
            self.wCount[werOut] -= 1
            self.wCount[werIn] += 1

            #werOutIdx = random.randint(0, self.totaalJuryNodig-1)
            #werIn = self.getRandomWer(self.totaalJuryNodig)
            #for w, jury in self.juryVoorWedstrijd.iteritems():
            #    if (werOutIdx < w.juryNodig): # juryNrId valt in deze wedstrijd
            #        werOut = jury[werOutIdx]
            #        for (wedstr, speler) in self.fixedJury:
            #            if (wedstr == w and werOut == speler):
            #                print "Probeer fixed w'er aan te passen : %s " % werOut.naam
            #                return
            #        print "%s vervangt %s" % (werIn.naam, werOut.naam)
            #        # update w'er
            #        self.juryVoorWedstrijd[w][werOutIdx] = werIn
            #        # update administratie
            #        self.wCount[werOut] -= 1
            #        self.wCount[werIn] += 1
            #        return
            #    else:  # juryNrId valt buiten deze wedstrijd -> ga door met de volgende
            #        werOutIdx -= w.juryNodig;
    def printWroosterPerWedstrijd(self):
        wedstr = []
        for w, jury in self.juryVoorWedstrijd.iteritems():
            wedstr.append((w,jury))
        wedstr = sorted(wedstr, key=lambda w: w[0].aanvang)
        for  w, jury in wedstr:
            juryTxt = ', '.join([s.naam for s in jury])
            print "%s %s - %s :  %s" % (time2str(w.aanvang), w.thuis.naam, w.uit.naam, juryTxt)
    def printWroosterPerPersoon(self, spelersMetW):
        wedstr = []
        for w, jury in self.juryVoorWedstrijd.iteritems():
            wedstr.append((w,jury))
        wedstr = sorted(wedstr, key=lambda w: w[0].aanvang)
        for s in spelersMetW:
            print "W rooster voor %s score: %d" % (s.naam, s.diffWithMeanScore)
            for w, jury in wedstr:
                for j in jury:
                    if j == s:
                        print "\t%s %s - %s" % (time2str(w.aanvang), w.thuis.naam, w.uit.naam)
    def printScores(self, spelersMetW):
        sw2 = spelersMetW[:]
        sw2 = sorted(sw2, key=lambda s: s.score)
        for s in sw2:
            print "%d voor %s (tijd: %s min)" % (s.diffWithMeanScore, s.naam, s.score)
    def toHTML(self, fname, spelersMetW, wedstrijden):
        wedstr = []
        for w, jury in self.juryVoorWedstrijd.iteritems():
            wedstr.append((w,jury))
        wedstr = sorted(wedstr, key=lambda w: w[0].aanvang)

        F = open(fname,"w")
        F.write('<html>\n')
        F.write('<body>\n')
        F.write('<h2>Rooster per wedstrijd</h2>\n')
        F.write("<table border=1>\n")
        F.write("  <tr><th>Aanvang</th><th>Wedstrijd</th><th>Jury1</th><th>Jury2</th><th>Jury3</th></tr>\n")
        for  w, jury in wedstr:
            juryTxt = '</td><td>'.join([s.naam for s in jury])
            F.write("  <tr><td>%s</td><td>%s - %s</td><td>%s</td></tr>\n" % (time2str(w.aanvang), w.thuis.naam, w.uit.naam, juryTxt))
        F.write("</table>\n")

        F.write("\n")
        F.write('<h2>Rooster per persoon</h2>\n')
        F.write("<table border=1>\n")
        F.write("  <tr><th>Naam</th><th>Aanvang</th><th>Wedstrijd</th></tr>\n")
        for s in spelersMetW:
            for w, jury in wedstr:
                for j in jury:
                    if j == s:
                        F.write("  <tr><td>%s</td><td>%s</td><td>%s - %s</td></tr>\n" % (s.naam, time2str(w.aanvang), w.thuis.naam, w.uit.naam))
        F.write("</table>\n")

        F.write("\n")
        F.write('<h2>Score per persoon</h2>\n')
        F.write("<table border=1>\n")
        F.write("  <tr><th>Naam</th><th>Score</th><th>Heeft w sinds</th><th>Reistijd</th></tr>\n")
        sw2 = spelersMetW[:]
        sw2 = sorted(sw2, key=lambda s: s.score)
        for s in sw2:
            F.write("  <tr><td>{naam}</td><td>{score}</td><td>{wstart}</td><td>{reistijd}</td></tr>\n".format(naam=s.naam, score=s.score, wstart=date2str(s.heeftWsinds), reistijd=s.reistijdNaarThuisWedstrijd))
        F.write("</table>\n")

        F.write("\n")
        F.write('<h2>Complete rooster</h2>\n')
        F.write("<table border=1>\n")
        F.write("  <tr><th>Nr</th><th>Aanvang</th><th>Wedstrijd</th><th>Jury</th></tr>\n")
        for wIdx, w in enumerate(wedstrijden):
            juryTxt = ""
            for w2, jury in wedstr:
                if w == w2:
                    juryTxt = ' & '.join([s.naam for s in jury])
            F.write("   <tr><td>#%d</td><td>%s</td><td>%s - %s</td><td>%s</td></tr>\n" % (wIdx, w.aanvang, w.thuis.naam, w.uit.naam, juryTxt))
        F.write("</table>\n")

        F.write('</body>\n')
        F.write('</html>\n')

    def printOnmogelijk(self):
        for s,w in self.onmogelijk:
            print "%s bij %s-%s op %s" % (s.naam, w.thuis.naam, w.uit.naam, time2str(w.aanvang))

    def Read(self, filename, app):
        stateNode = parse(filename).getElementsByTagName('state')[0]
        self.score = float(stateNode.getAttribute('score'))
        self.keerOnmogelijk = int(stateNode.getAttribute('keerOnmogelijk'))
        self.totaalJuryNodig = int(stateNode.getAttribute('totaalJuryNodig'))
        self.maxKeerWen = int(stateNode.getAttribute('maxKeerWen'))
        wedstrDOMs = stateNode.getElementsByTagName('wedstr')
        for wedstrDOM in wedstrDOMs:
            matchId = wedstrDOM.getAttribute('id')
            wedstr = app.GetWedstrijd(matchId)
            self.juryVoorWedstrijd[wedstr] = []
            juryDOMs = wedstrDOM.getElementsByTagName('jury')
            for juryDOM in juryDOMs:
                name = latin1_to_ascii(juryDOM.getAttribute('name'))
                j = app.FindOrAddSpeler(name)
                self.juryVoorWedstrijd[wedstr].append(j)
        onmogelijkDOMs = stateNode.getElementsByTagName('onmogelijk')
        for onmogelijkDOM in onmogelijkDOMs:
            matchId = onmogelijkDOM.getAttribute('wedstrId')
            wedstr = app.GetWedstrijd(matchId)
            name = latin1_to_ascii(onmogelijkDOM.getAttribute('juryName'))
            jury = app.FindOrAddSpeler(name)
            self.onmogelijk.append((jury, wedstr))
        wCountDOMs = stateNode.getElementsByTagName('wcount')
        for wCountDOM in wCountDOMs:
            name = latin1_to_ascii(wCountDOM.getAttribute('juryName'))
            jury = app.FindOrAddSpeler(name)
            cnt = int(wCountDOM.getAttribute('count'))
            self.wCount[jury] = cnt
        fixedJuryDOMs = stateNode.getElementsByTagName('fixedJury')
        for fixedJuryDOM in fixedJuryDOMs:
            matchId = fixedJuryDOM.getAttribute('wedstrId')
            wedstr = app.GetWedstrijd(matchId)
            name = latin1_to_ascii(fixedJuryDOM.getAttribute('juryName'))
            jury = app.FindOrAddSpeler(name)
            self.fixedJury.append((wedstr, jury))

    def Write(self, filename):
        wedstr = []
        for w, jury in self.juryVoorWedstrijd.iteritems():
            wedstr.append((w,jury))
        wedstr = sorted(wedstr, key=lambda w: w[0].aanvang)
        F = open(filename,"w")
        F.write('<state score="{score}" keerOnmogelijk="{onmogelijk}" totaalJuryNodig="{juryNodig}" maxKeerWen="{maxKeerWen}" >\n'.format(
                    score=self.score, onmogelijk=self.keerOnmogelijk, juryNodig=self.totaalJuryNodig, maxKeerWen=self.maxKeerWen
        ))
        for  w, jury in wedstr:
            F.write('  <wedstr id="{id}">\n'.format(id=w.matchId))
            for j in jury:
                F.write('    <jury name="{naam}" />\n'.format(naam= j.naam))
            F.write('  </wedstr>\n')
        for speler, wedstr in self.onmogelijk:
            F.write('  <onmogelijk juryName="{naam}" wedstrId="{id}" />\n'.format(naam=speler.naam, id=wedstr.matchId))
        for speler, cnt in self.wCount.iteritems():
            F.write('  <wcount juryName="{naam}" count="{cnt}" />\n'.format(naam=speler.naam, cnt=cnt))
        for (wedstr, speler) in self.fixedJury:
            F.write('  <fixedJury juryName="{naam}" wedstrId="{id}" />\n'.format(naam=speler.naam, id=wedstr.matchId))
        F.write('</state>\n')
        F.close()

class Application:
    def __init__(self, seizoenStartJaar, dataFile, wedstrijdenFile):
        # initialize data
        self.beginDatum = datetime(seizoenStartJaar , 9, 1)
        self.eindDatum = datetime(seizoenStartJaar+1, 5, 1)
        self.thuisBad = 'zuidlaren-aqualaren'
        self.teams = []
        self.spelers = []
        self.wedstrijden = []

        self.parseTeamsEnSpelers(dataFile)
        #self.bespreektijd("Heren2", 15, 15)
        self.parseWedstrijden2(wedstrijdenFile)

        self.wedstrijden = [w for w in self.wedstrijden if w.aanvang <= self.eindDatum]            # alleen wedstrijden voor einddatum

        self.wedstrijden = sorted(self.wedstrijden, key=lambda w: w.aanvang)                  # sorteer alle wedstrijden
        for s in self.spelers:
            s.verwerkWedstrijdRooster(self.wedstrijden, self.thuisBad)
        self.thuisWedstrijden = [w for w in self.wedstrijden if w.locatieCode == self.thuisBad]    # lijst van thuis wedstrijden waarvoor jury benodigd is
        spelersMetWkeys = {}
        d = self.beginDatum
        while d < self.eindDatum:
            wers = self.getWersAtDate(d)
            for w in wers:
                spelersMetWkeys[w] = 0
            d += timedelta(1,0)
        self.spelersMetW = spelersMetWkeys.keys()

    def FindOrAddTeam(self, alias, teamNaam, printOnCreation = False):
        for t in self.teams:
            if t.naam == alias or t.alias == alias:
                return t
        if printOnCreation:
            print "Onbekend team toegevoegd : %s (%s)" % (teamNaam, alias)
        t = Team(teamNaam, alias)
        self.teams.append(t)
        return t

    def FindOrAddSpeler(self, spelerNaam, printOnCreation = True):
        for s in self.spelers:
            if s.naam == spelerNaam:
                return s
        if printOnCreation:
            print "Onbekende speler toegevoegd : %s" % spelerNaam
        s = Speler(spelerNaam, self.eindDatum)
        self.spelers.append(s)
        return s

    def GetWedstrijd(self, matchId):
        for w in self.wedstrijden:
            if w.matchId == matchId:
                return w
        print "Onbekende wedstrijd nummer: {nr}".format(nr=matchId)
        return 0

    def parseTeamsEnSpelers(self, fname):
        dom1 = parse(fname).getElementsByTagName('data')[0]
        spelersDom = dom1.getElementsByTagName('Spelers')[0].getElementsByTagName('Speler')
        for spelerDom in spelersDom:
            naam = latin1_to_ascii(spelerDom.getAttribute('name'))
            hasWt = spelerDom.getAttribute('hasWsince')
            s = Speler(naam, parseDate(hasWt))
            if (spelerDom.hasAttribute('Wtot')):
                s.heeftWtot = parseDate(spelerDom.getAttribute('Wtot'))
            if(spelerDom.hasAttribute('reistijdNaarThuisWedstrijd')):
                s.reistijdNaarThuisWedstrijd = int(spelerDom.getAttribute('reistijdNaarThuisWedstrijd'))
            self.spelers.append(s)

        teamsDom = dom1.getElementsByTagName('Teams')[0].getElementsByTagName('Team')
        for teamDom in teamsDom:
            naam = teamDom.getAttribute('name')
            alias = teamDom.getAttribute('alias')
            t = Team(naam, alias)
            self.teams.append(t)
            teamSpelersDom = teamDom.getElementsByTagName('Speler')
            for teamSpelerDom in teamSpelersDom:
                naam = latin1_to_ascii(teamSpelerDom.getAttribute('name'))
                start = teamSpelerDom.getAttribute('start')
                end = teamSpelerDom.getAttribute('end')
                if start=='':
                    st = datetime(2000,1,1)
                else:
                    st = parseDate(start)
                if end=='':
                    nd = datetime(2030,1,1)
                else:
                    nd = parseDate(end)
                s = self.FindOrAddSpeler(naam)
                capNr = 0
                if(spelerDom.hasAttribute('capNr')):
                    capNr = int(spelerDom.getAttribute('capNr'))
                role = 'speler'
                if(spelerDom.hasAttribute('speler')):
                    role = spelerDom.getAttribute('speler')
                s.addTeam(t, st, nd, capNr, role)

    def parseWedstrijden(self, fname):
        f = open(fname, 'r')
        for lineId, line in enumerate(f):
            if lineId == 0:
                continue
            (matchId, afd, aanvang, thuisNaam, uitNaam, zwembad, scheidsrechters) = latin1_to_ascii(line).split(';') # 7481;D1.DG2C;22-10-11 17:30;De Plons DG 1;Ritola Z & PC DG 1;De Bonte Wever - Assen (Assen );,  ;
            t1 = FindOrAddTeam(afd + '.' + thuisNaam, thuisNaam)
            t2 = FindOrAddTeam(afd + '.' + uitNaam, uitNaam)
            w = Wedstrijd(parseDateTime(aanvang), t1, t2, zwembad, afd, matchId, self.thuisBad)
            nieuweMatch = True
            for w2 in self.wedstrijden:
                if w2.thuis == w.thuis and w2.uit == w.uit and w2.aanvang == w.aanvang:
                    nieuweMatch = False
            if nieuweMatch:
                self.wedstrijden.append(w)

    def parseWedstrijden2(self, fname):
        f = open(fname, 'r')
        for lineId, line in enumerate(f):
            if lineId == 0:
                continue
            (aanvangDatum, aanvangTijd, plaats, zwembad, afd, matchId, thuisNaam, uitNaam) = latin1_to_ascii(line).split(',')
            uitNaam = uitNaam[:-1] # remove last character : "\n"
            t1 = self.FindOrAddTeam(afd + '.' + thuisNaam, thuisNaam)
            t2 = self.FindOrAddTeam(afd + '.' + uitNaam, uitNaam)
            zwembad2 = "{bad} ({plaats})".format(bad=zwembad, plaats=plaats)
            aanvang = parseDateTime("{datum} {tijd}".format(datum=aanvangDatum, tijd=aanvangTijd))
            w = Wedstrijd(aanvang, t1, t2, zwembad2, afd, matchId, self.thuisBad)
            nieuweMatch = True
            for w2 in self.wedstrijden:
                if w2.thuis == w.thuis and w2.uit == w.uit and w2.aanvang == w.aanvang:
                    nieuweMatch = False
            if nieuweMatch:
                self.wedstrijden.append(w)

    def printCurrentTeamsAndSpelers(self):
        vandaag = datetime.today()
        for t in self.teams:
            print t.naam
            for s in spelers:
                for (st, start, end, capNr, role) in s.teams:
                    if st == t and start <= vandaag and end > vandaag:
                        print "\t%s" % s.naam

    def printTeamRoosters(self):
        for t in self.teams:
            print t.naam
            for w in wedstrijden:
                if w.thuis == t:
                    print "\t               %s %s" % ( time2str(w.aanvang), w.uit.naam)
                if w.uit == t:
                    print "\t%s %s %s" % ( time2str(w.vertrek), time2str(w.aanvang), w.thuis.naam)

    def getWersAtDate(self, date):
        spelersMetW = []
        for s in self.spelers:
            if (s.heeftWsinds <= date and s.heeftWtot > date):
                spelersMetW.append(s)
        return spelersMetW

    def inproveState(self, initState, stepsRemain = 1000):
        currentState = initState
        currentState.calculateScore(self.spelersMetW)
        nWersToUpdate = 1
        global onmogelijkScore
        tempFactor = 0.0000005 # float(onmogelijkScore/150)
        while stepsRemain > 0:
            updatedState = currentState.clone(self.spelersMetW)
            updatedState.calculateScore(self.spelersMetW)
            if nWersToUpdate > 0:
                updatedState.shuffle2Wers(self.eindDatum, self)
            updatedState.calculateScore(self.spelersMetW)
            ht = math.log(2.0)/(stepsRemain*tempFactor)
            print "%05d : [%d met %d onm] vs [%d met %d onm] stephalf : %4.2f " % (stepsRemain, currentState.score, currentState.keerOnmogelijk, updatedState.score, updatedState.keerOnmogelijk, ht)
            if updatedState.score <= currentState.score: # or updatedState.keerOnmogelijk < currentState.keerOnmogelijk:
                currentState = updatedState.clone(self.spelersMetW)
            else:
                r = random.random()
                us = updatedState.score
                cs = currentState.score
                dif = us+1-cs
                temp = math.exp(-float(dif)/(stepsRemain*tempFactor))
                if temp > r: # and updatedState.keerOnmogelijk < currentState.keerOnmogelijk:
                    currentState = updatedState.clone(self.spelersMetW)
            stepsRemain -= 1
            del updatedState
        currentState.printOnmogelijk()
        return currentState

    def bespreektijd(self, teamnaam, voorMinuten, naMinuten):
        t = FindOrAddTeam(teamnaam, "")
        t.minutenVoorbespreken = voorMinuten
        t.minutenNabespreken = naMinuten

    def generateRooster(self, nInits = 1, nIters = 5000):
        self.overallBestState = State(self.spelersMetW)
        for _ in range(nInits):
            currentState = State(self.spelersMetW)
            currentState.FixJury(self.FindOrAddSpeler("Joanne Polling"), [ self.wedstrijden[4], self.wedstrijden[11], self.wedstrijden[12], self.wedstrijden[13] ])
            currentState.FixJury(self.FindOrAddSpeler("Marleen Speelman"), [ self.wedstrijden[4], self.wedstrijden[9] ])
            currentState.FixJury(self.FindOrAddSpeler("Anja Speelman"), [ self.wedstrijden[9] ])
            currentState.FixJury(self.FindOrAddSpeler("Ilona Tent"), [ self.wedstrijden[4] ])
            currentState.FixJury(self.FindOrAddSpeler("Heleen Alsema"), [ self.wedstrijden[9] ])
            currentState.FixJury(self.FindOrAddSpeler("Vincent van der Wijk"), [ self.wedstrijden[3] ])
            currentState.FixJury(self.FindOrAddSpeler("Marcel van Doren"), [ self.wedstrijden[3] ])
            currentState.FixJury(self.FindOrAddSpeler("Kees Schouten"), [ self.wedstrijden[3] ])
            currentState.FixJury(self.FindOrAddSpeler("Gjalt Bearda"), [ self.wedstrijden[8], self.wedstrijden[11], self.wedstrijden[12], self.wedstrijden[13] ])
            currentState.FixJury(self.FindOrAddSpeler("Pjotr Svetachov"), [ self.wedstrijden[8] ])
            currentState.FixJury(self.FindOrAddSpeler("Henk van Calker"), [ self.wedstrijden[8], self.wedstrijden[11], self.wedstrijden[12], self.wedstrijden[13] ])
            currentState.randomInit(self.thuisWedstrijden, self.spelers, self.spelersMetW, self)
            bestState = self.inproveState(currentState, nIters)
            if bestState.keerOnmogelijk == 0 and bestState.score < self.overallBestState.score:
                self.overallBestState = bestState.clone(self.spelersMetW)

    def readState(self, filename):
        self.overallBestState = State(self.spelersMetW)
        self.overallBestState.Read(filename, self)

    def writeState(self, filename):
        self.overallBestState.Write(filename)

    def writeResults(self, wfile):
        #self.spelersMetW = sorted(self.spelersMetW, key=lambda s: s.naam)
        #overallBestState.printWroosterPerPersoon(self.spelersMetW)
        #overallBestState.printWroosterPerWedstrijd()
        print "------best state--------"
        self.overallBestState.calculateScore(self.spelersMetW)
        self.overallBestState.printScores(self.spelersMetW)
        print "------onmogelijk in best state ----------"
        self.overallBestState.printOnmogelijk()
        self.overallBestState.toHTML(wfile, self.spelersMetW, self.wedstrijden)

#app = Application(2013, 'data.xml', '2013-2014.csv')
#app.readState('out/state.csv')
##app.generateRooster(1, 50)
#app.writeState('out/state2.csv')
#app.writeResults('out/wrooter.html')

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Create rooster based files for Ritola Z&PC")
    parser.add_argument("year", type=int, help="year of the season to calcuate (2013=2013-2014)")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-o", "--openStateFile", help="File to load the state from")
    parser.add_argument("-s", "--simulate", action="store_true", help="Run simulated annealing")
    parser.add_argument("-g", "--imporveWRoosterSteps", type=int, help="Number of simulated annealing steps to improve the state", default=5000)
    parser.add_argument("-r", "--improveWRoosterRuns", type=int, help="Number of simulated annealing runs", default=1)
    parser.add_argument("-w", "--writeStateFile", help="File to write the state new file to")
    parser.add_argument("-d", "--dirForWebdata", help="directory to write webdata to")
    args = parser.parse_args()

    seizoen = "{}-{2}".format(args.year, args.year+1)




