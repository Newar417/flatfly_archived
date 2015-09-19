import json, os, sys, datetime, time, urllib, websocket, operator, random, re
from colorama import Fore, Style, init   ; init()
  
t0 = time.time() ; Z = 0 ; nboutputs = 0 ; nbinputs = 0
VERBOSE = 1

print 'chainsnort v0.484: ' , 
os.system('title chainsnort_inspect [mainnet]')
matches = open('prefixes.txt').read().split()
matches2 = ['111111','XXXXXX']  

mini_easter_egg = ['** THANKS! **    (' +chr(3)+ ' _ ' +chr(3)+ ')        ','** PEACE! **     (^ _ ^)        ']


class Plex(object):
    def __init__(self, name):
        self.file = open(name, 'w')
        self.stdout = sys.stdout
        sys.stdout = self
    def __del__(self):
        sys.stdout = self.stdout
        self.file.close()
    def write(self, data):
     
        self.stdout.write(data)
        data=data.replace(chr(8),'')
        data=data.replace(chr(0x1B),'')
        data=re.sub('\[.*m','',data)
        # data=re.sub('\t ','X', data)

        self.file.write(data)


def main():
  global Z, btcseen
  btcseen = 0
  
  while (1):
    bigtag = '  '
    result = ws.recv()
    time.sleep(0.05)
    result = json.loads(result)
    if result['op'] == 'block' :
      print
      reward = result['x']['reward']/1e8	  	
      print datetime.datetime.utcnow().strftime("%H:%M:%S.%f")[:-3] , bigtag + ' {:11.4f}'.format(reward) ,'B  [NEW BLOCK SOLVED] ' ,
      print Fore.CYAN+Style.BRIGHT + str(result['x']['height']) + Fore.RESET+Style.NORMAL
      print 
      continue 
	  	  
    inputs = sum(p['prev_out']['value'] for p in result['x']['inputs']  )
    outputs = sum(p['value'] for p in result['x']['out']  )
    feepaid = (inputs-outputs)/1e8 
    val = sum(p['value'] for p in result['x']['out'])/1e8
    btcseen = btcseen + val
	
    if val >= 50:
     if val >= 5000:
      print '\a' ,
     bigtag = Fore.GREEN+Style.BRIGHT + '>>' #  + chr(16)*2 
     time.sleep(0.3)
	 
    feetag = ''
    if feepaid < 0.0001 or feepaid >= 0.01:  
     feetag = Fore.YELLOW+Style.BRIGHT	
	
    if VERBOSE == 0:
        max_addr = sorted(result['x']['out'], key=operator.itemgetter('value'), reverse=True)[0]['addr']
        for ku in result['x']['out']:
         if any(s in ku['addr'] for s in matches):
           max_addr =  Fore.MAGENTA+Style.BRIGHT + max_addr + Fore.RESET+Style.NORMAL
             
        print '\b'+ datetime.datetime.utcnow().strftime("%H:%M:%S.%f")[:-3], bigtag + ' {:11.4f}'.format(val) ,'B '  + Fore.RESET+Style.NORMAL , max_addr , '\t' , feetag ,  '\b'*6 + '{:12.8f}'.format(feepaid) + Fore.RESET+Style.NORMAL
   
    if VERBOSE == 1:
       nboutputs = 0 ; nbinputs = 0 
	   
       for ki in result['x']['inputs']:
           print ' '.ljust(30) , 'i', ki['prev_out']['addr']
           nbinputs += 1
       for ku in result['x']['out']:
           print ' '.ljust(30) , 'o', ku['addr']
           nboutputs += 1

       txcat =  ''  
       if any(s['prev_out']['addr'] in ku['addr'] for s in result['x']['inputs']):    
           txcat = '[WEB_SPEND]'
       if nboutputs > 2: 
 		   txcat = '[AUTOMATED_PAYMENT]'
		   if (nboutputs > 20) & (nbinputs == 1):
		       txcat = '[FAUCET_PAYMENT]'
		       if val >= 0.2: 
		           txcat = '[MIXER]'
		       if val >= 20:
		           txcat = '[MININGPOOL_PAYMENT]'
       if (val >= 50) & (nbinputs == 1): 
 		   txcat = '[COLDSTORAGE_MOVE]'
       if (val <= 0.0011) & (nbinputs == 1): 
 		   txcat = '[MICROTRANSACTION]'		   
       if (nboutputs == 1) & (nbinputs == 1): 
 		   txcat = '[ADDRESS_SWEEP]'
       if (nboutputs == 1) & (nbinputs > 1): 
 		   txcat = '[ADDRESS_CONSOLIDATION]'      
       if txcat == '':  
           txcat = '[NATIVE_SPEND]'
       for ku in result['x']['out']:
           if any(s in ku['addr'] for s in matches) | ('1Lucky' in result['x']['inputs'][0]) :    # to fix
               txcat +=    ' [ONCHAIN_GAMING]'           # or in inputs as well
               break 
       for ku in result['x']['out']:
           if any(s in ku['addr'] for s in matches2):
               txcat = '[COIN_DESTRUCTION]'      # also add DONATION
               break
       for ku in result['x']['out']:
           if ku['value'] < 546:   
               txcat = '[ILLEGAL]'
               break               
       for ku in result['x']['out']:
           if ku['value'] == 7800:
               if (nboutputs == 3):		   
                  txcat = '[XCP_OP]'
               # print '\a'
               break   

       for ku in result['x']['out']:
           if ku['addr'][0] == '3':   
               txcat = Fore.CYAN+Style.BRIGHT + '[MULTISIG]'
               break 
               			  
       print 'Transaction:   ' + result['x']['hash'] 
			 
       print '\b'+ datetime.datetime.utcnow().strftime("%H:%M:%S.%f")[:-3], bigtag + ' {:11.4f}'.format(val) ,'B '  + Fore.RESET+Style.NORMAL , Fore.RESET+Style.BRIGHT + txcat.ljust(32) + Fore.RESET+Style.NORMAL , ' ', feetag , '{:12.8f}'.format(feepaid) + Fore.RESET+Style.NORMAL
 
    Z += 1 ; print
 
try:
  sys.tracebacklimit = 0
  domain='blockchain.info'
  stat = int(urllib.urlopen('https://'+domain+'/q/24hrtransactioncount').read().decode("utf8"))
  print Fore.CYAN+Style.BRIGHT + '\b' + str(stat)  + Fore.RESET+Style.NORMAL +  ' new transactions in the last 24 hours  -  ' + Fore.CYAN+Style.BRIGHT  + '%02.02f' % (stat/86400.0) + Fore.RESET+Style.NORMAL + ' tx/sec' 
  # print '\nEstablishing TLS tunnel...',  
  print '\nCapturing transactions on mainnet...  (Fingerprinting enabled)\r',  
  ws = websocket.create_connection("wss://ws."+domain+"/inv")
  ws.send('{"op":"unconfirmed_sub"}')  ;
  ws.send('{"op":"blocks_sub"}')
  # print 'Done. Waiting for new transactions...\r',
   
  if '-o' in sys.argv:
       Plex('../../../Log/txtrace.log')       
  
  time.sleep(0.3)
  main()
      
except KeyboardInterrupt:
  t1 = time.time()
  print
  print 'Closing threads... Done.'
  print 'Captured',Z, 'events - Transaction density: %02.02f' % (Z/(t1 - t0)) , 'tx/sec - Coins moved:' + ' {:5.4f}'.format(btcseen) 
  sys.exit()

