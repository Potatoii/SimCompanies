import math
from datetime import datetime

# retail_model
retail_model = {
    'fnc': 'Quadratic',
    'xMultiplier': 0.151206,
    'yMultiplier': 0.168467,
    'yOffset': 4669.223051,
    'xOffsetBase': -681.109714,
    'marketSaturationDiv': 0.027323,
    'power': 2
}

# executives(去除isCandidate)
executives = [{'id': 3537673, 'name': 'Kai Artemov', 'age': 39, 'gender': 'M', 'genome': 'male-01-0-0-0-4-1',
               'currentEmployer': 3534319, 'isCandidate': False, 'created': '2023-11-13T01:28:33.121430+00:00',
               'accelerated': False, 'salary': 1945, 'strikeUntil': None,
               'skills': {'coo': 1, 'cfo': 1, 'cmo': 14, 'cto': 3}, 'position': 'cmo',
               'start': '2023-11-13T13:27:41.419866+00:00', 'positionAccelerated': False, 'currentTraining': None},
              {'id': 3672815, 'name': 'Marit Scherbo', 'age': 25, 'gender': 'F', 'genome': 'female-01-0-2-1-1-3',
               'currentEmployer': 3534319, 'isCandidate': False, 'created': '2023-12-11T14:43:35.592034+00:00',
               'accelerated': False, 'salary': 2006, 'strikeUntil': None,
               'skills': {'coo': 4, 'cfo': 0, 'cmo': 0, 'cto': 1}, 'position': 'coo',
               'start': '2023-12-12T00:44:18.229406+00:00', 'positionAccelerated': False, 'currentTraining': None},
              {'id': 3546911, 'name': 'Kaori Ballangrud', 'age': 38, 'gender': 'F', 'genome': 'female-01-2-2-1-0-1',
               'currentEmployer': 3534319, 'isCandidate': False, 'created': '2023-11-15T00:10:46.455980+00:00',
               'accelerated': False, 'salary': 1087, 'strikeUntil': None,
               'skills': {'coo': 1, 'cfo': 9, 'cmo': 0, 'cto': 4}, 'position': 'cfo',
               'start': '2023-11-23T05:08:39.428546+00:00', 'positionAccelerated': False, 'currentTraining': None},
              {'id': 3582440, 'name': 'Gunde Patzaichin', 'age': 34, 'gender': 'M', 'genome': 'male-04-0-4-0-5-0',
               'currentEmployer': 3534319, 'isCandidate': False, 'created': '2023-11-22T12:31:07.578690+00:00',
               'accelerated': False, 'salary': 2000, 'strikeUntil': None,
               'skills': {'coo': 4, 'cfo': 5, 'cmo': 3, 'cto': 16}, 'position': 'cto',
               'start': '2023-11-23T05:08:45.270861+00:00', 'positionAccelerated': False, 'currentTraining': None}]

# salesModifier
salesModifier = 3
recreationBonus = 0


def vz(e, t, r, i, n, o, s):
    l = i8(e, 100, t, r, i, n, o, s)
    return 100 * 3600 / l


def i8(e, t, r, i, n, o, s, l):
    u = o - 0.3 if o < 0.3 else o
    d = max(u - n * 0.24, 0.1 - 0.24 * 2)
    p = zwr(e, d, t, i) / s / l
    return p - p * r / 100


def zwr(e, t, r, i):
    return (math.pow(i * e['xMultiplier'] + (e['xOffsetBase'] + (t - .5) / e['marketSaturationDiv']), e['power']) * e[
        'yMultiplier'] + e['yOffset']) * r


def Gwr(e, t, r):
    i = Ul(t) if t else []
    n = qn(i, "cmo")
    return (e or 0) + math.floor(n / 3) + r


def qn(e, t):
    return math.floor(
        sum([r['skills'][t] if r['position'] == t else r['skills'][t] / 4 if r['position'][0] == "c" else 0 for r in
             e]))


def Ul(e):
    t = datetime.now().timestamp() * 1000
    r = [o['id'] for o in zTe(e, t)]
    i = [o['id'] for o in WTe(e, t)]
    n = [o['id'] for o in GTe(e, t)]
    return [o for o in e if o['id'] not in r and o['id'] not in n and o['id'] not in i]


def zTe(e, t):
    n = 60 * 60 * 3 * 1e3
    return [r for r in e if
            r['position'][0] == "c" and t - datetime.timestamp(datetime.fromisoformat(r['start'])) * 1000 < n and not r[
                'positionAccelerated'] and not r[
                'isCandidate']]


def GTe(e, t):
    return [r for r in e if r['strikeUntil'] and datetime.strptime(r['strikeUntil'], '%Y-%m-%dT%H:%M:%S.%f%z') > t]


def WTe(e, t):
    n = 60 * 60 * 27 * 1e3
    return [r for r in e if r['currentTraining'] and not r['currentTraining']['accelerated'] and datetime.strptime(
        r['currentTraining']['datetime'], '%Y-%m-%dT%H:%M:%S.%f%z') > t - n]


unitsAnHour = vz(retail_model, Gwr(salesModifier, executives, recreationBonus), 5142.785228951256, 2,
                 1.1960499259160826, 1, 2)  # 加速倍数, 建筑等级

print(unitsAnHour)
