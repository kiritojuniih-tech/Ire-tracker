"""Ire Tracker local backend. Python 3.10+; no dependencies."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, quote
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import json, os, pathlib, time, threading

ROOT = pathlib.Path(__file__).resolve().parent
KEY = os.environ.get('RIOT_API_KEY','').strip()
REGION='https://americas.api.riotgames.com'
PLATFORM='https://br1.api.riotgames.com'
CACHE = {}
CACHE_LOCK = threading.Lock()
CACHE_SECONDS = int(os.environ.get('CACHE_SECONDS', '300'))

def riot(base,path):
    req=Request(base+path,headers={'X-Riot-Token':KEY,'Accept':'application/json','User-Agent':'IreTracker/0.4'})
    with urlopen(req,timeout=15) as r: return json.load(r)

def build_uncached(count):
    if not KEY: raise ValueError('Configure RIOT_API_KEY antes de sincronizar.')
    account=riot(REGION,'/riot/account/v1/accounts/by-riot-id/Ire%20Lorun/br%201')
    puuid=account['puuid']
    summoner=riot(PLATFORM,'/lol/summoner/v4/summoners/by-puuid/'+quote(puuid))
    league=riot(PLATFORM,'/lol/league/v4/entries/by-puuid/'+quote(puuid))
    ids=riot(REGION,'/lol/match/v5/matches/by-puuid/'+quote(puuid)+'/ids?start=0&count='+str(count))
    matches=[]
    for mid in ids:
        try:
            m=riot(REGION,'/lol/match/v5/matches/'+quote(mid))
            info=m['info']; p=next(x for x in info['participants'] if x['puuid']==puuid)
            matches.append({'id':mid,'champion':p.get('championName','?'),'win':p.get('win',False),'kills':p.get('kills',0),'deaths':p.get('deaths',0),'assists':p.get('assists',0),'cs':p.get('totalMinionsKilled',0)+p.get('neutralMinionsKilled',0),'gold':p.get('goldEarned',0),'duration':info.get('gameDuration',0),'role':p.get('teamPosition',''),'queue':info.get('queueId',0),'date':info.get('gameCreation',0),'items':[p.get('item'+str(i),0) for i in range(7)]})
        except (HTTPError,KeyError,StopIteration,URLError): continue
    return {'account':{'name':account.get('gameName','Ire Lorun'),'tag':account.get('tagLine','br 1'),'level':summoner.get('summonerLevel'),'icon':summoner.get('profileIconId')},'ranked':league,'matches':matches,'updatedAt':int(time.time())}

def build(count):
    now = time.time()
    with CACHE_LOCK:
        saved = CACHE.get(count)
        if saved and now - saved['cached_at'] < CACHE_SECONDS:
            return saved['data']
        data = build_uncached(count)
        CACHE[count] = {'data': data, 'cached_at': time.time()}
        return data

class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs): super().__init__(*args,directory=str(ROOT),**kwargs)
    def do_GET(self):
        parsed=urlparse(self.path)
        if parsed.path=='/api/status': return self.send_json({'configured':bool(KEY),'server':'BR1','region':'AMERICAS'})
        if parsed.path=='/api/profile':
            try:
                count=min(20,max(1,int(parse_qs(parsed.query).get('count',['10'])[0])))
                return self.send_json(build(count))
            except HTTPError as e:
                return self.send_json({'error':{401:'Chave inválida.',403:'Chave expirada ou sem permissão.',404:'Conta ou recurso não encontrado.',429:'Limite de requisições da Riot atingido.'}.get(e.code,'Erro da Riot: '+str(e.code))},e.code if e.code in (401,403,404,429) else 502)
            except (ValueError,URLError,KeyError) as e: return self.send_json({'error':str(e)},400)
        return super().do_GET()
    def send_json(self,obj,status=200):
        data=json.dumps(obj,ensure_ascii=False).encode()
        self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)

if __name__=='__main__':
    print('Ire Tracker: http://localhost:8765')
    ThreadingHTTPServer(('0.0.0.0',int(os.environ.get('PORT','8765'))),Handler).serve_forever()
