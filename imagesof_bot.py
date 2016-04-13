import os
import time
import praw
import re
import requests
from datetime import datetime

#regex to match urls that aren't allowed domains
urlregex = r"(\.jpg|\.jpeg|\.png|\.gif|\.gifv|\.apng|\.tiff|\.bmp|\.pdf|\.xcf)$"
#regex for all the allowed domains
domainregex = r"^(500px\.com|abload\.de|cdn\.theatlantic\.com|.*\.deviantart\.com|.*\.deviantart\.net|fav\.me|.*\.fbcdn\.net|.*\.files\.wordpress\.com|flic\.kr|flickr\.com|forgifs\.com|gfycat\.com|(.*\.)?gifsoup\.com|(.*\.)?gyazo\.com|(.*\.)?imageshack\.us|imgclean\.com|(i\.)?imgur\.com|instagr\.am|instagram\.com|(cdn\.)?mediacru\.sh|(.*\.)?media\.tumblr\.com|(.*\.)?min\.us|(.*\.)?minus\.com|(.*\.)?panoramio\.com|photoburst\.net|(.*\.)?photoshelter\.com|pbs\.twimg\.com|(.*\.)?photobucket\.com|picsarus\.com|puu\.sh|scontent\.cdninstagram\.com|(.*\.)?staticflickr\.com|(.*\.)?tinypic\.com|twitpic\.com|upload.wikimedia\.org)"
#fires up praw and reddit, and identifies the bot
r = praw.Reddit('ImagesOf v5.1 /u/amici_ursi')
#identifies the stream of submissions that we're going swim in.
submission_stream = praw.helpers.submission_stream(r, 'all')

#get's all the blacklists. these need to be publicly viewable because praw bugs out on private wiki pages
print("Getting global user blacklist")
globaluserblacklist_wiki = r.get_wiki_page("ImagesOfNetwork","userblacklist")
globaluserblacklist = set([name.strip().lower()[3:] for name in globaluserblacklist_wiki.content_md.split("\n") if name.strip() != ""])
print(globaluserblacklist)
print("Getting global subreddit blacklist")
globalsubredditblacklist_wiki = r.get_wiki_page("ImagesOfNetwork","subredditblacklist")
globalsubredditblacklist = set([name.strip().lower()[3:] for name in globalsubredditblacklist_wiki.content_md.split("\n") if name.strip() != ""])
print(globalsubredditblacklist)
print("Getting California subreddit blacklist")
californiasubredditblacklist_wiki = r.get_wiki_page("ImagesOfCalifornia","subredditblacklist")
californiasubredditblacklist = set([name.strip().lower()[3:] for name in californiasubredditblacklist_wiki.content_md.split("\n") if name.strip() != ""])
print(californiasubredditblacklist)
print("Getting China subreddit blacklist")
chinasubredditblacklist_wiki = r.get_wiki_page("ImagesOfChina","subredditblacklist")
chinasubredditblacklist = set([name.strip().lower()[3:] for name in chinasubredditblacklist_wiki.content_md.split("\n") if name.strip() != ""])
print(chinasubredditblacklist)
print("Getting India subreddit blacklist")
indiasubredditblacklist_wiki = r.get_wiki_page("ImagesOfIndia","subredditblacklist")
indiasubredditblacklist = set([name.strip().lower()[3:] for name in indiasubredditblacklist_wiki.content_md.split("\n") if name.strip() != ""])
print(indiasubredditblacklist)

#searches the stream for all the criteria
def search_for_places(r):
    print("searching for posts...")
    for post in submission_stream:
    #afghanistan
        swim(r,
            submission = post,
            goodregex = r"(\bafghanistan\b|\bkabul\b|\bbamyan\b|\bkandahar\b|\bbamyan province\b|\bherat\b|\bband-e amir national park\b|\bjalalabad\b|\bmazar-i-sharif\b|\bpaghman\b|\bkunduz\b|\bghazni\b|\bbalkh\b|\bbaghlan province\b|\bsistan\b|\bbagram\b|\bbadghis province\b|\bkhost\b|\blashkar gah\b|\bfayzabad\b|\bmaymana\b|\bpuli khumri\b|\bsheberghan\b|\bfarah\b|\btalogan\b|\bsamangan\b|\bcharikar\b|\bmes aynak\b|\bsange-e-masha\b)",
            postinto = "imagesofafghanistan",
            getfromthese = {'afghanistan', 'afghanistanpics'}
            )
    #alabama
        swim(r,
            submission = post,
            goodregex =  r"(\balabama\b|\balabami?ans?\b|\bbirmingham\b(al|alabama)\b|\bmontgomery\b(al|alabama)\b|\bmobile\b(alabama|al)\b|\bhuntsville\b(alabama|al)\b|\btuscaloosa\b|\bhoover\b(alabama|al)\b|\bdothan\b|\bdecatur\b|\bauburn\b|\bmadison\b(al|alabama)\b)",
            badregex = r"(\bpoppy montgomery\b|\bmaine\b|\b(ashley|bailee) madison\b|\bmadison wisconsin\b|\balabama hills\b|\bal jazeera\b)",
            badcaseregex = r"(\bal\b)",
            postinto = "imagesofalabama",
            getfromthese = {'alabama', 'huntsvillealabama', 'birmingham', 'montgomery', 'mobileal', 'tuscaloosa', 'auburn', 'florenceal', 'rolltide', 'wde', 'capstone', 'uah', 'uab', 'asms'}
            )
    #alaska
        swim(r,
            submission = post,
            goodregex = r"(\balaska\b|\bak\b|\balaskans?\b|\banchorage\b|\bfairbanks\b|\bdenali national park\b|\bketchikan\b|\bskagway\b|\bkenai fjords\b|\bmendenhall glacier\b|\bjuneau\b|\beagle river\b|\bbadger\b(alaska|ak)\b|\bknik\-fairview\b|\bcollege\b(alaska|ak)\b|\bsitka\b|\blakes\b(alaska|ak)\b|\btanaina\b(alaska|ak)\b)",
            badregex = r"(\bmalamute\b|\balaskan salmon\b|\bDouglas Fairbanks\b|ak.?47|ak.?107,|\bak-|\brupaul\b|\bcable anchorage\b|\bbaked alaskan?\b)",
            badcaseregex = r"(\bak\b|\bAk\b|\baK\b)",
            smallsubredditblacklist = {'rupaulsdragrace', 'rpdrcirclejerk'},
            postinto = "imagesofalaska",
            getfromthese = {'alaska', 'alaskanporn', 'alaskabeer', 'akgaming', 'anchorage', 'uaa', 'fairbanks', 'skagway', 'juneau', 'uasjuneau', 'yukon', 'kodiak'}
            )
    #arizona
        swim(r,
            submission = post,
            goodregex = r"(\barizona\b|\baz\b|\barizoni?ans?\b|\bgrand\bcanyon\b|\bphoenix\b(arizona|az)\b|\btucson\b|\bmesa\b(arizona|az)\b|\bchandler\b(arizona|az)\b|\bglendale\b(arizona|az)\b|\bscottsdale\b|\bgilbert\b(arizona|az)\b|\bsitka\b|\btempe\b|\bpeoria\b|\bsedona\b|\bantelope canyon\b|\bhavasu falls\b|\bhoover dam\b|\bdesert botanical garden)",
            badregex = r"(\barizona (robins|tea)\b|\bhyundai tucson\b)",
            smallsubredditblacklist = {'themsfightinherds', 'mylittlepony', 'kia'}, 
            postinto = "imagesofarizona",
            getfromthese = {'arizona', 'phoenix', 'tucson', 'flagstaff', 'prescott', 'tempe', 'bisbee', 'cochise', 'asu', 'nau', 'uofarizona', 'azdiamondbacks', 'azcardinals', 'suns', 'coyotes', 'arizonapolitics', 'arizonabeer'}
            )
    #arkansas
        swim(r,
            submission = post,
            goodregex = r"(\barkansas\b|\barkansasans?\b|\bhot springs national park\b|\bcrystal bridges museum\b|\bclinton presidential center\b|\bgarvan woodland gardens\b|\blittle\brock\b|\bfort\bsmith\b|\bfayetteville\b|\bspringdale\b(arkansas|ar)\b|\bjonesboro\b|\bnorth\blittle\brock\b|\bconway\b|\brogers\b|\bpine\bbluff\b|\bbentonville\b)",
            badregex = r"(\bar-\b|\b(ga|georgia)\b|\b(m\.?(iste)?r\.?|nathan) rogers\b)",
            smallsubredditblacklist = {'ar15'},
            postinto = "imagesofarkansas",
            getfromthese = {'arkansas', 'universityofarkansas', 'lyoncollege', 'hendersonstate', 'uca', 'asu_jonesboro', 'uafs', 'ualr', 'uam', 'ozarka', 'razorbacks', 'fayetteville', 'littlerock', 'fortsmith', 'jonesboro', 'texarkana', 'conwayar', 'arkieoutdoors', 'arkansashomeschoolers'}
            )
    #australia
        swim(r,
            submission = post,
            goodregex = r"(\baustralia\b|\bsydney\b|\bmelbourne\b|\bperth\b|\bbrisbane\b|\bgold coast\b|\bcairns\b|\badelaide\b|\bfraser island\b|\bcanberra\b|\bport douglas\b|\bmargaret river\b|\bkakadu national park\b|\bhobart\b|\bsunshine coast\b|\bbroome\b|\bphillip island\b|\bbarossa valley\b|\bbyron bay\b|\blaunceston\b|\bkangaroo island\b|\bsurgers paradise\b|\bwollongong\b|\btownsville\b|\bexmouth\b|\bcape tribulation\b|\bblue mountains national park\b|\bkuranda\b|\bmoreton island\b|\bcoffs harbour\b|\brockhampton\b|\bmandurah\b|\bpemberton\b|\bhervey bay\b|\bcentral coast\b|\btamworth\b|\bbowen\b|\bbunbury\b|\bbrisbane\b|\bbrusselton\b|\bgrampians national park\b|\bnorth stradbroke island\b|\bkalbarri\b|\btoowoomba\b|\bport arthur\b|\bbundaberg\b|\bgeelong\b|\bmount gambier\b|\bport jackson\b|\bsydney\b|\bmelbourne\b|\bgreat ocean road\b|\bbondi beach\b|\buluru\b|\bgreat barrier reef\b|\bkings park\b|\bmanly beach\b|\btaronga zoo\b|\bkakadu national park\b|\bfraser island\b|\bhunter region\b|\bwhitsunday islands?\b|\bshrine of remembrance\b|\bnoosa national park\b|\bwhitehaven beach\b|\bquestacon\b|\badelaide zoo\b|\blake burley griffin\b|\bnational gallery of victoria\b|\bhealesville santuary\b|\bwilsons promontory\b|\bsea world gold coast\b|\bcurrumbin wildlife sanctuary\b|\bgrampians national park\b|\bbarossa valley\b|\bburleigh heads\b|\bdaintree rainforest\b|\bcape tribulation\b|\bcapitol theatre\b|\btamborine mountain\b|\badelaide botanic garden\b|\bshelly beach\b|\bmount ainslie)",
            badregex = r"(\bsydney sierota\b|\bflorida\b|\bfl\b|\bport chester\b|\bnew york\b|\bny\b|\bcalifornia\bca\b)",
            postinto = "imagesofaustralia",
            getfromthese = {'australia', 'australiapics', 'adelaide', 'askanaustralian', 'australianagriculture', 'afl', 'australiantelevision', 'aleague', 'australiagonewild', 'ausbeer', 'ballarat', 'ausbike', 'bluemountains', 'ausbookexchange', 'brisbane', 'canberra', 'cairns', 'carsaustralia', 'circlejerkaustralia', 'centralcoastnsw', 'centralqueensland', 'cquni', 'darwinaustralia', 'doublej', 'drugsaustralia', 'ausecon', 'australianev', 'auselt', 'ausents', 'ausenviro', 'ausfemalefashion', 'australianfilm', 'australianfilmmakers', 'ausfinance', 'fishingaustralia', 'ausfood', 'ausfreebies', 'aufrugal', 'geelong', 'goldcoast', 'ausguns', 'aussiehiphop', 'australianhistory', 'hobart', 'aushomebrew', 'koalas', 'koalasgonewild', 'auslaw', 'libertarianaustralia', 'australianmakeup', 'melbourne', 'melbournemusic', 'melbtrade', 'ausmemes', 'australianmfa', 'ausmetal', 'modelaustralia', 'modelparliament', 'ausmotoring', 'australianmilitary', 'ausmusic', 'nbn', 'netflixaustralia', 'newcastle', 'nrl', 'northqueensland', 'outdooraus', 'paulkelly', 'perth', 'australianpolitics', 'auspol', 'austpropertyponzi', 'queensland', 'australiarebooted', 'regionalaustralia', 'aussieriders', 'australianright', 'r4raustralia', 'r4rbris', 'r4rmelbourne', 'r4rperth', 'r4rsydney', 'savethenbn', 'ausskincare', 'australiasnow', 'startupsaustralia', 'straya', 'ausstocks', 'sunshinecoast', 'sydney', 'sydneymusic', 'tasmania', 'austechsupport', 'townsville', 'triplej', 'tweedshire', 'vego', 'warrnambool', 'westernaustralia', 'wollongong', 'ausmemes'}
            )
    #belgium
        swim(r,
            submission = post,
            goodregex = r"(\bbelgium\b|\bbelgians?\b|\bbruges\b|\bbrussels\b|\bantwerp\b|\bghent\b|\bli(è|e)ge\b|\bdinant\b|\bnamur\b|\bypres\b|\bmons\b|\bcharleroi\b|\bbastogne\b|\bdurbuy\b|\bostend\b|\bleuven\b|\bbouillon\b|\bwaterloo\b|\bmiddelkerke\b|\bgenk\b|\barlon\b|\bla roche-en-ardenne\b|\bmechelen\b|\bblankenberge\b|\bveurne\b|\bstavelot\b|\bmalmedy\b|\bvielsalm\b|\bchimay\b|\bverviers\b|\brochefort\b|\bknokke-heist\b|\bdamme\b|\bbinche\b|\bmaaseik\b|\bzeebrugge\b|\bmaasmechelen\b|\bde haan\b|\bde panne\b|\bwavre\b|\bvoeren\b|\btournai\b|\boudenaarde\b|\bkoksijde\b|\bhan-sur-lesse\b|\bpoperinge|\bath\b|\bNeufch(â|a)teau\b|\bBelgian Luxembourg\b|\bs(ain)?t bavo'?s cathedral\b|\bghen\b|\bmusical instrument museum\b|\bcathedral of s(ain)?t michael\b|\batomium\b|\bbasilica of the holy blood\b|\bmanneken pis\b|\bcinquantenaire\b|\bplantin-moretus museum\b|\bhorta museum\b|\bgravensteen\b|\bpairi daiza\b|\bflanders fields museum\b|\bcathedral of our lady\b|\bb(e|é)guinage\b)",
            badregex = r"(\bbrussels sprouts?\b|\bcanada\b|\bcambridge\b|\buniversity of waterloo\b|\bvan damme\b\\bbelgian.waffles?\b|\blondon\b|\bindiana\b|\bontario\b|\bwaterloo bridge\b)",
            badcaseregex = r"(\bATH\b|\bath\b|\bIN\b|\bON\b)",
            postinto = "imagesofbelgium",
            getfromthese = {'belgium', 'bruges', 'gent', 'brussels', 'leuven', 'belgiumpics'}
            )
    #belize
        swim(r,
            submission = post,
            goodregex = r"(\bbelize\b|\bambergris caye\b|\bcaye caulker\b|\bxunantunich\b|\blamanai\b|\bgreat blue hole\b|\bcaracol\b|\bactun tunichil muknal\b|\bcockscomb basin\b|\bhol chan\b|\bsan ignacio resort\b|\bbaron bliss light\b|\bguanacastle national park\b|\bsan pedro\b|\bplacencia\b|\bsan ignacio\b|\bbelmopan\b|\bpunta gorda\b|corozal town\b|\bdangriga\b|\borange walk town\b|\bcrooked tree wildlife sanctuary\b|\bmountain pine ridge forest reserve\b|\bbenque viejo del carmen\b|\bcaye chapel\b|\bladyville\b|\bs(ain)?t herman's blue hole\b|\brio bravo conservation\b|\bspanish lookout\b|\bturneffe atoll\b|\bcorozal bay\b|\bhattieville\b|\broaring creek\b|\bindependence and mango creek\b|\brockstone pond\b|\bla democracia\b)",
            postinto = "imagesofbelize",
            getfromthese = {'belize', 'belizepics'}
            )
    #brazil
        swim(r,
            submission = post,
            goodregex = r"(\bbra(s|z)il\b|\brio de janeiro\b|\bs(a|ã)o paulo\b|\bsalvador\b|\bfoz do igua(c|ç)u\b|\bfortaleza\b|\bcuritiba\b|\bnatal\b|\bflorian(ó|o)polis\b|\bmanaus\b|\brecife\b|\bbras(í|i)lia\b|\bMacei(o|ó)\b|\bArma(c|ç)(a|ã)o dos B(u|ú)zios\b|\bporto seguro\b|\bbelo horizonte\b|\bgramado\b|\bJo(a|ã)o Pessoa\b|\bporto alegre\b|\bBel(e|é)m\b|\bsantos\b|\bbonito\b|\baracaju\b|\bs(a|ã)o lu(í|i)s\b|\bVit(ó|o)ria\b|\bparaty\b|\bouro preto\b|\bBalne(a|á)rio Cambori(u|ú)\b|\bCampos do Jord(a|ã)o\b|\bilha grande\b|\bpipa beach\b|\bpetr(ó|o)polis\b|\bilhabela\b|\bilh(é|e)us|\bsantar(e|é)m\b|\bCuiab(a|á)\b|\bangra dos reis\b|\bcampinas\b|\bubatuba\b|\bjijoca de jericoacoara\b|\bpo(ç|c)os de caldas\b|\b cabo frio\b|\btijuca forest\b|\bcaldas novas\bmaragogi\b|\bfavela\b|\bcampo grande\b|\bguaruj(a|á)\b|\bteresina\b|\bchrist the redeemer\b|\bsugarloaf mountain\b|\bcorcovado\b|\biguazu falls\b|\bcopacabana\b|\bipanema\b|\bmaracan(a|ã) stadium\b|\bibirapuera park\b|\bamazon theatre\b|\bteatro municipal\b|\bsanta teresa\b|\barpoador\b|\btijuca forest\b|\blen(c|ç)ois maranhenses\b|\bpaulista avenue\b|\bbotanical garden of curitiba\b|\bleblon\b|\binhotim\b|\bchapada diamantina national park\b|\bfort copacabana\b|\bmuseum of the portuguese language\b|\bescadaria selar(ó|o)n\b|\bparque lage\b|\btheatro municipal\b|\bporto de galinhas\b|\bsambadrome Marqu(e|ê)s de Sapuca(i|í)\b|\bchurch of nosso senhor do bonfim\b|\bmeeting of waters\b|\bpal(a|á)cio da alvorada\b|\bcathedral of bras(í|i)lia\b|\bporto da barra beach\b|\bmuseu paulista\b|\bwire opera house\b|\bcandel(a|á)ria church\b|\bluz station\b|\bmaraj(ó|o)\b|\bbeto carrero world\b|\bchapada dos veadeiros\b|\bcanoa quebrada\b|\bbasilica of the national shrine of our Lady of Aparecida\b|\bhopi hari)",
            postinto = "imagesofbrazil",
            badregex = r"(\\bsalvador dal(i|í)\b|\bel salvador\b)",
            getfromthese = {'brasil', 'brasilpics', 'brazilpics', 'alagoas', 'amapa', 'amazonas', 'aracaju', 'bahia', 'belempa', 'belohorizonte', 'brasilia', 'campinas', 'carioca', 'ceara', 'cuiaba', 'curitiba', 'espiritosanto', 'fortaleza', 'goiania', 'goias', 'ilhabela', 'jaraguadosul', 'maceio', 'manaus', 'maranhao', 'minasgerais', 'paraiba', 'parana', 'pelotas', 'pernambuco', 'piaui', 'portoalegre', 'portovelho', 'recife', 'riobranco', 'riodejaneiro', 'riograndedosul', 'rondonia', 'roraima', 'salvador', 'saocarlos', 'saopaulo', 'sergipe', 'tocantins'}
            )
    #california
        swim(r,
            submission = post,
            goodregex = r"(\bcalifornia\b|\bca\b|\bcalifornians?\b|\bSan Bernardino\b|\blos angeles\b|\bsan diego\b|\bsan jose\b|\bsan francisco\b|\bfresno\b|\bsacramento\b|\blong beach\b|\boakland\b|\bbakersfield\b|\banaheim\b|\byosemite\b|\bnapa valley\b|\buniversal studios hollywood\b)",
            badregex = r"(rain(s|ed|ing)|driv(e|ing)|traffic|ca\.|ca glue|\bphillipines\b|\banaheim pepper\b)",
            badcaseregex = r"(\bca\b|\bCa\b|\bcA\b)",
            smallsubredditblacklist = californiasubredditblacklist,
            postinto = "imagesofcalifornia",
            getfromthese = {'california', 'californiapics', 'calipornia'}
            )
    #canada
        swim(r,
            submission = post,
            goodregex = r"(\bcanada\b|\btoronto\b|\bvancouver\b|\bmontreal\b|\bquebec city\b|\bottawa\b)",
            badregex = r"(\bWA\b|\bwashington\b|\bcanada water library\b)",
            postinto = "imagesofcanada",
            getfromthese = {'canada', 'alberta', 'britishcolumbia', 'manitoba', 'newbrunswickcanada', 'newfoundland', 'nwt', 'novascotia', 'nunavut', 'ontario', 'pei', 'quebec', 'saskatchewan', 'yukon', 'barrie', 'brampton', 'burlingtonon', 'calgary', 'durham', 'edmonton', 'fredericton', 'guelph', 'halifax', 'hamilton', 'kelowna', 'kingstonontario', 'kitchener', 'lethbridge', 'londonontario', 'mississauga', 'moncton', 'montreal', 'niagara', 'ottawa', 'peterborough', 'regina', 'saskatoon', 'stjohnsnl', 'sudbury', 'thunderbay', 'toronto', 'vancouver', 'victoriabc', 'waterloo', 'whistler', 'windsorontario', 'winnipeg', 'calgaryflames', 'edmontonoilers', 'habs', 'ottawasenators', 'leafs', 'canucks', 'winnipegjets', 'teamcanada', 'torontoraptors', 'torontobluejays', 'montrealimpact', 'tfc', 'whitecapsfc', 'cfl', 'canadianpostsecondary', 'fundraisingcanada', 'canadapolitics', 'canadianforces', 'canadia', 'canp41s1', 'cbc_radio', 'ocanada', 'immigrationcanada', 'francophonie'}
            )
    #chile
        swim(r,
            submission = post,
            goodregex = r"(\bchile\b|\bsantiago\b|\btorres del paine\b|\bvalpara(i|í)so\b|\bpunta arenas\b|\bsan pedro de atacama\b|\bpuerto montt\b|\biquique\b|\barica\b|\bchilo(é|e) island\b|\bVi(n|ñ)a del Mar\b|\bPuc(o|ó)n\b|\bpuerto varas\b|\bpuetro natales\b|\bantofagasta\b|\bla serena\b|\bconcepci(o|ó)n\b|\btemuco\b|\bosorno\b|\bchill(a|á)n\b|\bcoyhaique\b|\bcalama\b|\bvillarrica\b|\brobinson crusoe island\b|\bfrutillar\b|\blos andes\b|\blauca national park\b|\bcopiap(ó|o)\b|\brancagua\b|\b(lake san rafael|san rafael lake)\b|\bcaldera\b|\bla campana\b|\btalca\b|\bConguill(í|i)o\b|\bpichilemu\b|\balgarrobo\b|\bpuerto williams\b|\bpuerto chacabuco\b|\bsanta cruz\b|\bprovidencia\b|\bsan felipe\b|\bpanguipulli\bolmu(e|é)\b|valle nevado\b|\bancud\b|\bhuilo-huilo\b|\bCuric(ó|o)\b|\bchile chico\b|\btorres del paine\b|\bsan Crist(o|ó)bal\b|\blauca national park\b|\bvalle de la luna\b|\bsantiago metropolitan park\b|\bla moneda palace\b|\bplaza de armas\b|\bLos Pingüinos\b|\bmagdalena island\b|\bmuseo chileno de arte precolombino\b|\bsan rafael glacier\b|\bsanta Luc(i|í)a\b|\bCaj(o|ó)n del Maipo|\bmuseum of memory and human rights\b|\bvalle nevado\b|\bchilean national museum of fine arts\b|\bvillarrica\b|\bcordillera paine\b|\bparque forestal\b|\bcostanera center\b|\bosomo\b|\bhumberstone and santa laura saltpeper works\b|\bChungar(a|á)\b|\bttodos los santos\b|\bel morado\b|\bfantasilandia\b|\bsan rafael lake\b|\bcentro cultural palacio de la moneda\b|\bojos del salado\b|\bpumalin park\b|\bConguill(i|í)o national park\b|\bvillarrica lake\b|\bchilean national zoo\b|\bbosque de fray jorge national park\b|\bbeagle channel\b|\bcasa colorada\b|\bPukar(a|á) de quitor\b|\bRe(n|ñ)aca beach\b|\bcalbuco\b|\bEstaci(o|ó)n Mapocho\b|\btronador\b|\bgrey glacier\b|\blake Peho(e|é)\b|\bpuyehue lake\b|\bojos del caburgua\b|\bPuntiagudo-Cord(o|ó)n Cenizos\b|\bchurch of san pedro de atacama\b|\bFitz Roy\b|\bchalt(e|é)n\b|\bandes\b|\beaster island\b|\bw(e|é)on\b|\bcerro castillo\b|\bcarlos ib(a|á)(ñ|n)ez\b|\bla paz\b|\bdynevor\b|\bmapuche\b|\bchilla\b|\bla silla\b|\batacama\b|\bel potre chico\b)",
            badregex = r"(\bcalifornia\b|\bca\b|\bbolivia\b|\bargentina\b|\bindiana\b|\bspain\bcamino de santiago\b)",
            badcaseregex = r"(\bchile\b)",
            smallsubredditblacklist = {'food', 'foodporn', 'supremeclothing','caldera'},
            postinto = "imagesofchile",
            getfromthese = {'Santiago', 'LaRoja', 'ChilENTs', 'ChileCringe', 'ChileCirclejerk', 'TopMusicChile'}
            )
    #china
        swim(r,
            submission = post,
            goodregex = r"(\bchina\b|\bbeijing\b|\bshanghai\b|\bguangzhou\b|\bxi'an\b|\bshenzhen\b)",
            badregex = r"(\b(from|made in) china\b|\bchina harbor\b|\bshanghai gp3\b)",
            smallsubredditblacklist = californiasubredditblacklist,
            postinto = "imagesofchina",
            getfromthese = {'china', 'chinapics', 'chinaart'}
            )
    #colorado
        swim(r,
            submission = post,
            goodregex = r"(\bcolorado\b|\bco\b|\bcoloradans?\b|\brocky mountain national park\b|\bestes park\b|\bpikes peak\b|\bgarden of the gods\b|\bcheyenne mountain zoo\b|\bmesa verde national park\b|\bdenver\b|\bcolorado\bsprings\b|\baurora\b(co|colorado)\b|\bfo?r?t\bcollins\b|\blakewood\b|\bthornton\b|\bpueblo\b|\barvada\b|\bwestminster\b|\bcentennial\b(colorado|co)\b)",
            badregex = r"(co-|aurora borealis|co.?worker|co\.|\/co\/|\bthornton state\b|\bdenver harbor\b|\bwestminster (abbey|bridge)\b|\b(chevy|chevrolet) colorado\b|\b\&co\b|\b\& co\b|\bnc\b|\bnorth carolina\b)",
            badcaseregex = r"(\bCo\b|\bco\b|\bcO\b)",
            smallsubredditblacklist = {'trees', 'london', 'panthers'},
            postinto = 'imagesofcolorado',
            getfromthese = {'colorado', 'cowx', 'denverpics'}
            )
    #connecticut
        swim(r,
            submission = post,
            goodregex = r"(\bconnecticut\b|\bct\b|\bconnecticuters?\b|\bmystic seaport\b|\blake compounce\b|\bgillette castle state park\b|\bmark twain house\b|\bmystic aquarium and institute\b|\bbridgeport\b|\bnew\bhaven\b|\bhartford\b|\bstamford\b|\bwaterbury\b|\bnorwalk\b|\bdanbury\b|\bnew\bbritain\b)",
            badregex = r"(\bct.(scan|machine|unit)\b|\bc(onnecticu)?t river\b|\bct-|\b(a|p)\.?m\.? ct\b)",
            badcaseregex = r"(\bCt\b|\bct\b|\bcT\b)",
            postinto = 'imagesofconnecticut',
            getfromthese =  {'connecticut', 'movingtoCT', 'ctbeer', 'newhaven', 'hartford', 'UCONN', 'stamfordct', 'oldsaybrook', 'connecticutkayakers', 'SoNo', 'ctjobs', 'wcsu', 'WaterburyCT', 'subaru_ct', 'enfieldct', 'EasternCT', 'milford', 'ConnecticutR4R', 'woodburyCT', 'tolland', 'norwalk'}
            )
    #delaware
        swim(r,
            submission = post,
            goodregex = r"(\bdelaware\b|\bdelwarans?\b|\bwilmington\b|\bhagley museum\b|\bnemours mansion\b|\bcape henlopen\b|\bdover\b|\bnewark\b(de|delaware)\b|\bbear\b\b(delaware|de)\b|\bmiddletown\b|\bbrookside\b|\bGlasgow\b(de|delaware)\b|\bHockessin\b|\bpike\bcreek\bvalley\b|\bSmyrna\b)",
            badregex = r"(\bnew jersey\b|\bnj\b|\bwilmington island\b|\bwilmington.*\b(nc|north carolina)\b|\bdover bridge\b)",
            smallsubredditblacklist = {'easternshoremd'},
            postinto = 'imagesofdelaware',
            getfromthese = {'delaware'}
            )
    #england
        swim(r,
            submission = post,
            goodregex = r"(\bengland\b|\blondon\b|\boxford\b|\bmanchester\b|\bnew castle upon tyne\b|\bbirmingham\b|\byork\b|\bcambridge\b|\bwindsor\b|\bcanterbury\b|\bbrighton\b|\bbristol\b|\bleeds\b|\bnew forest\b|\bstraford-upon-avon\b|\bnottingham\b|\bbournemouth\b|\bgreenwich\b|\bportsmouth\b|\bpeak district\b|\bsheffield\b|\bwarwick\b|\bexeter\b|\bsalisbury\b|\byorkshire dales\b|\bnewquay\b|\bgreater manchester\b|\blake district national park\b|\bleicester\b|\bwindermere\b|\bkeswick\b|\bharrogate\b|\bwinchester\b|\bcheltenham\b|\bpeterborough\b|\bsouthport\b|\bpenrith\b|\bglastonbury\b|\bashford\b|\bmilton keynes\b|\bcoventry\b|\bcolchester\b)",
            badregex = r"(\bnew england\b|\bpete ashford\b|\bnew york\b|\bcanterbury tales\b|\balabama\b|\bal\b|\bconnecticut\b|\bct\b|\bpalin\b|\bmassachusetts\b|\bma\b|\bn(orth)? carolina\b|\bnc\b|\bontario\b|\bcanada\b|\bdevon windsor\b|\bdean winchester\b|\boxford english dictionary\b)",
            badcaseregex = r"(\bON\b|\boN\b)",
            smallsubredditblacklist = {'londonontario', 'newzealand', 'nascar', 'guns', 'gunporn', 'hunting', 'supremeclothing', 'birmingham', 'fo4', 'ockytop', 'boston'},
            postinto = 'imagesofengland',
            getfromthese = {'england', 'englandpics'}
            )
    #florida
        swim(r,
            submission = post,
            goodregex = r"(\bflorida\b|\bfl\b|\bFloridians?\b|\bjacksonville\b|\bmiami\b|\btampa\b|\bSaint\bPetersburg\b|\borlando\b|\bHialeah\b|\bTallahassee\b|\bFo?r?t\bLauderdale\b|\bPort\bSaint\bLucie\b|\bPembroke\bPines\b)",
            badregex = r"(\bfl studios?\b)",
            smallsubredditblacklist = {'edmprodcirclejerk', 'edmproduction'},
            postinto = 'imagesofflorida',
            getfromthese =  {'florida', 'floridabrew', 'miabeer', 'jaxbeer', 'soflabeer', 'tampabaybeer'}
            )
    #france
        swim(r,
            submission = post,
            goodregex = r"(\bfrance\b|\bparis\b|\bmarseille\b|\bcannes\b|\bstrasbourg\b|\btoulouse\b|\beiffel tower\b|\blouvre\b|\bfrench riviera\b|\barc de triomphe\b|\bversailles\b|\bMusée d'Orsay\b|\bSacré-C(oe|œ)ur\b|\bjardin du luxembourg\b)",
            badregex = r"(\bparis (tx|texas|island|hilton|dylan)\b|\bbrian france\b)",
            postinto = 'imagesoffrance',
            getfromthese = {'france', 'francepics'}
            )
    #georgia
        swim(r,
            submission = post,
            goodregex = r"(\bgeorgia\b|\bga\b|\bGeorgians?\b|\batlanta\b|\bcolumbus\b(georgia|ga)\b|\bSavannah\b|\bathens\b(ga|georgia)\b|\bsandy\bsprings\b|\bmacon\b|\broswell\b(ga|georgia)\b|\balbany\b(ga|georgia)\b|\bjohns\bcreek\b|\bwarner\brobins\b)",
            badregex = r"(\bgeorgia graham\b|\brepublic of georgia\b)",
            badcaseregex = r"(\bga\b|\bgA\b)",

            postinto = 'imagesofgeorgia',
            getfromthese = {'georgia'}
            )
    #guatemala
        swim(r,
            submission = post,
            goodregex = r"(\bguatemala\b|\btikal\b|\bLake Atitl(á|a)n\b|\bpacaya\b|\bdulce river\b|\blake Pet(é|e)n Itz(á|a)|\bpet(é|e)n department\b|\bpanajachel\b|\bcobán\b)",
            postinto = 'imagesofguatemala',
            getfromthese = {'guatemala'}
            )
    #hawaii
        swim(r,
            submission = post,
            goodregex = r"(\bhawaii\b|\bHawaiians?\b|\bHonolulu\b|\bpearly\bcity\b|\bhilo\b|\bkailua\b|\bWaipahu\b|\bKaneohe\b|\bMililani\bTown\b|\bKahului\b|\bEwa\bGentry\b|\bwarner\brobins\b|kihei\b)",
            badregex = r"(\bhawaiian rolls?\b)",
            postinto = 'imagesofhawaii',
            getfromthese = {'hawaii', 'maui', 'kauai', 'bigisland', 'oahu', 'honolulu', 'hawaiijobs', 'universityofhawaii', 'bicyclehawaii', 'hawaiigardening', 'himusic', 'hawaiipics'}
            )
    #hongkong
        swim(r,
            submission = post,
            goodregex = r"(\bhong kong\b|\bvictoria peak\b|\blantao island\b|\bNgong Ping\b|\bPo Lin Monastery\b|\blamma island\b|\bcheung chao\b)",
            postinto = 'imagesofhongkong',
            getfromthese = {'hongkong', 'hongkongpics'}
            )
    #iceland
        swim(r,
            submission = post,
            goodregex = r"(\biceland\b)",
            postinto = 'imagesoficeland',
            getfromthese = {'iceland', 'island'}
            )
    #idaho
        swim(r,
            submission = post,
            goodregex = r"(\bidaho\b|\bIdahoans?\b|\bboise\b|\bnampa\b|\bMeridian\b|\bIdaho\bFalls\b|\bPocatello\b|\bCaldwell\b|\bCoeur\bd'Alene\b|\bTwin\bFalls\b|\blewiston\b)",
            badregex = r"(\bidaho springs\b)",
            postinto = 'imagesofidaho',
            getfromthese = {'idaho'}
            )
    #illinois
        swim(r,
            submission = post,
            goodregex = r"(\billinois\b|\bIllinoisans?\b|\bIL\b|\bchicago\b|\bAurora\b(IL|Illinois)\b|\brockford\b|\bJoliet\b|\bnaperville\b|\bspringfield\b|\bpeopria\b|\belgin\b(IL|illinois)\b|\bWaukegan\b)",
            badregex = r"(\bil\b|\bIl\b|\biL\b|\bchicago('s)? pizza\b)",
            smallsubredditblacklist = {'thesimpsons', 'guns'},
            postinto = 'imagesofillinois',
            getfromthese = {'illinois'}
            )
    #india
        swim(r,
            submission = post,
            goodregex = r"(\bindian?\b|\bbharat\b|\bhindustan\b|\bbharatiya\b|\bhindu\b|\bgoa\b|\bmumbai\b|\bnew delhi\b|\bbengaluru\b|\bchennai\b|\bjaipur\b|\bhyderabad\b|\bagra\b|\bkolkata\b|\bpondicherry\b|\booty\b|\bshimla\b|\bdarjeeling\b|\bkochi\b|\bmunnar\b|\budaipur\b|\bmysore\b|\bmanali\b|\bmanali\b|\bhimachal pradesh\b|\bpune\b|\bvaranasi\b|\bkodaikanal|\bleh\b|\bthiruvananthapuram\b|\bnainital\b|\bahmedabad\b|\bgangtok\b|\bchandigarh\b|\bamritsar\b|\bsrinagar\b|\bjodhpur\b|\bjaisalmer\b|\bmadurai\b|\bkanyakumari\b|\bcoimbatore\b|\bvisakhapatnam\b|\brishikesh\b|\balappuzha\b|\bmangalore\b|\bmahabaleshwar\b|\bdharamsala\b|\bharidwar\b|\bmussoori\b|\bkovalam\b|\bshillong\b|\bindore\b|\b(mount|mt)\babu\b|\bdehradun\b|\bp(or)?t blair\b|\bandhra pradesh\b|\bbihar\b|\bchhattisgarh\b|\bgoa\b|\bgujarat\b|\bharyana\b|\bhimachal pradesh\b|\bjammu and kashmir\b|\bjharkhand\b|\bkarnataka\b|\bkerala\b|\bmadhya pradesh\b|\bmaharashtra\b|\bodisha\b|\bpunjab\b|\barunachal pradesh\b|\bassam\b|\bmanipur\b|\bmeghalaya\b|\bmizoram\b|\bnagaland\b|\bsikkim\b|\btripura\b|\brajasthan\b|\btamil nadu\b|\btelangana\b|\buttar pradesh\b|\buttarakhand\b|\bwest bengal\b|\badaman islands?\b|\bnicobar islands?\b|\bchandigarh\b|\bdadra haveli\b|\bnagar haveli\b|\bdaman and diu\b|\blakshadweep\b|\bdelhi\b|\bpuducherry\b|\bpondicherry\b|\buttaranchal\b|\barunachal\b|\bandhra\b|\bmadhya bharat\b|\borissa\b)",
            badregex = r"(\bgoa crew\b|\bgoa'uld\b|\bamerican?\b|\bwest punjab\b|\bindiamain\b|\bindia ink\b|\bindian ink\b|\bIndia de Beaufort\b|\bmilf\b|porn|\bescort\b|\bindian chief\b)",
            smallsubredditblacklist = indiasubredditblacklist,
            postinto = 'imagesofindia',
            getfromthese = {'india', 'indianfoodporn', 'jammukashmir', 'andhrapradesh', 'bihar', 'chhattisgarh', 'goa', 'gujarat', 'haryana', 'himachalpradesh', 'jammu', 'kashmir', 'jharkhand', 'karnataka', 'kerala', 'madhyapradesh', 'maharashtra', 'odisha', 'punjab', 'arunachal', 'assam', 'northeastindia', 'manipur', 'mizoram', 'nagaland', 'sikkim', 'rajasthan', 'tamilnadu', 'telangana', 'uttarpradesh', 'uttarakhand', 'andamannicobarislands', 'chandigarh', 'lakshadweep', 'delhi', 'newdelhi', 'pondicherry', 'india', 'askindia', 'bestofindia', 'bharat', 'dealsforindia', 'indiamain', 'inindiannews', 'atheismindia', 'indianautos', 'indianents', 'indianfitness', 'indiainvestments', 'indianleft', 'indianmythology', 'indianpolitics', 'indianstartups', 'ecigindia', 'indianwriters', 'lgbtindia', 'oldindia', 'republicofindia', 'royalenfield', 'southasia', 'southasianart', 'southasianhistory', 'travelsinindia', 'incredibleindia', 'indianbooks', 'mpoi', 'tilinindia', 'agra', 'allahabad', 'asansol', 'bangalore', 'bareilly', 'bhopal', 'chandigarh', 'chennai', 'coimbatore', 'dehradun', 'durgapur', 'delhi', 'hyderabad', 'jamshedpur', 'kochi', 'kolhapur', 'kolkata', 'lucknow', 'mumbai', 'nagpur', 'nashik', 'pune', 'trivandrum', 'vijaywada', 'assam', 'gujarat', 'karnataka', 'kerala', 'rajasthan', 'tamilnadu', 'uttarakhand', 'westbengal', 'indianbands', 'icm', 'ipm', 'indianindie', 'bollywood', 'indiancinema', 'kollywood', 'bollywoodtrailers', 'bengalilanguage', 'hindi', 'indiareads', 'kannada', 'marathi', 'pali', 'punjabi', 'sahitya', 'sanskrit', 'tamil', 'telugu', 'urdu', 'desiads', 'indiangaming', 'desicringe', 'desihumor', 'indianpics', 'wtfindia', 'indiancomicbooks', 'trollywood', 'desishowerthoughts', 'ghatisongs', 'angrezinewspapers', 'ipl', 'indiansports', 'indianfootball', 'agra', 'ahmedabad', 'aizawl', 'ajmer', 'aligarh', 'allahabad', 'almora', 'amritsar', 'anand', 'asansol', 'aurangabad', 'bangalore', 'bareilly', 'bengaluru', 'bharuch', 'bhilai', 'bhopal', 'bhubaneswar', 'bombay', 'chandigarh', 'chennai', 'coimbatore', 'darjeeling', 'dehradun', 'delhi', 'dharamsala', 'dombivli', 'durgapur', 'faridabad', 'gandhinagar', 'ghaziabad', 'gurgaon', 'guwahati', 'gwalior', 'hyderabad', 'imphal', 'indore', 'jabalpur', 'jaipur', 'jalandhar', 'jamshedpur', 'jodhpur', 'kalyan', 'kanpur', 'kochi', 'kolhapur', 'kolkata', 'kozhikode', 'leh', 'lonavala', 'lucknow', 'ludhiana', 'madras', 'mathura', 'meerut', 'mohali', 'mumbai', 'nagpur', 'nainital', 'nashik', 'navimumbai', 'newdelhi', 'noida', 'pondicherry', 'pune', 'raipur', 'rajkot', 'ranchi', 'sangli', 'satara', 'shimla', 'srinagar', 'trivandrum', 'udaipur', 'vadodara', 'varanasi', 'vasai', 'vijaywada', 'indianews', 'indiamain', 'indiapolicy', 'indiancoins', 'desigifs', 'isro', 'antrixcorporation', 'indiandefense', 'indianfood', 'indianrightwing', 'abcdesis', 'desiweddings', 'indianpeoplegifs', 'notthepyaaz', 'indianblogrecipes', 'nri', 'indiansuperleague', 'indianstandupcomedy', 'indianhistory', 'desifoodies', 'classicalindian', 'mfaindia', 'sitar', 'nmmusicindia'}
            )
    #indiana
        swim(r,
            submission = post,
            goodregex = r"(\bindiana\b|\bIndianians?\b|\bhoosiers?\b|\bIndianapolis\b|\bF(or)?t\bWayne\b|\bevansville\b|\bsouth\bbend\b|\bhammond\b|\bbloomington\b|\bgary\bindiana\b|\bcarmel\bindiana\b|\bfishers\bindiana\b|\bmuncie\b)",
            badregex = r"(\bindiana jones\b)",
            postinto = 'imagesofindiana',
            getfromthese = {'indiana'}
            )
    #iowa
        swim(r,
            submission = post,
            goodregex = r"(\biowa\b|\bIowans?\b|\bdes moines\b|\bcedar rapids\b|\bdavenport\b|\bsioux city\b|\bwaterloo (IA|iowa)\b|\bcouncil bluffs\b|\bames\b|\bDubuque\b)",
            badregex = r"(\b(kennedy|adam) davenport\b|\bca\b|\bcalifornia\b)",
            smallsubredditblacklist = {'toronto'},
            postinto = 'imagesofiowa',
            getfromthese = {'iowa'}
            )
    #iran
        swim(r,
            submission = post,
            goodregex = r"(\biran\b|\btehran\b|\bmashhad\b|\bshiraz\b|\bisfahan\b|\btabriz\b|\byazd\b|\bqeshm\b|\bkashan\b)",
            postinto = 'imagesofiran',
            getfromthese = {'iran', 'iranpics'}
            )
    #isleofman
        swim(r,
            submission = post,
            goodregex = r"(\bisle of man\b|\bcastle rushen\b|\bpeel castle\b|\bcalf of man\b|\bleece museum\b|\bsnaefell\b|\blangness peninsula\b|\bpeel cathedral\b|\bsouth barrule|\bmaughold head\b|\bbradda hill\b|\bnorth barrule\b|\bchicken rock\b|\bmull hill\b|\bspanish head\b|\bcastletown\b|\bporn erin\b|\bramsey\b)",
            badregex = r"(\b(aaron|gordon|laura|steve|geoff|the|mega|kelly).ramsey\b)",
            smallsubredditblacklist = {'ck2gameofthrones', 'gameofthrones', 'hbogameofthrones', 'soccer', 'gunners', 'fantasypl'},
            postinto = 'imagesofisleofman',
            getfromthese = {'isleofman'}
            )
    #japan
        swim(r,
            submission = post,
            goodregex = r"(\bjapan\b|\btokyo\b|\bkyoto\b|\bm(oun)?t\bfuji\b|\bmeiji shrine\b|\bkinkaku-ji\b|\bkiyomizu-dera\b|\bsenso-ji\b|\bosaka\b|\bnagoya\b|\bhakone\b)",
            badregex = r"(\btokyo (ghoul|mew)\b)",
            postinto = 'imagesofjapan',
            getfromthese = {'japan', 'japanpics', 'normaldayinjapan'}
            )
    #kansas
        swim(r,
            submission = post,
            goodregex = r"(\bkansas\b)",
            postinto = 'imagesofkansas',
            getfromthese = {'kansas', 'placesubreddit2'}
            )
    #kentucky
        swim(r,
            submission = post,
            goodregex = r"(\bkentucky\b)",
            postinto = 'imagesofkentucky',
            getfromthese = {'kentucky'}
            )
    #libya
        swim(r,
            submission = post,
            goodregex = r"(\blibyan?\b|\btripoli\b|\bleptis magna\b|\bbenghazi\b|\btobruk\b|\bghadames\b|\bshahhat\b|\bsabha\b|\bsabratha\b|\bzuwarah\b|\bgharyan\b|\bkhoms\b|\bghat\b|\bal ayda\b|\bsirte\b|\bmisurata\b|\bzawiya\b|\bbani walid\b|\bzintan\b|\bjanzur\b|\bdarnah\b|\bzliten\b|\bmarj\b|\bajdabiya\b|\bsirte district\b|\bnalut\b|\b ra's lanuf\b|\bmurzuq district\b|byafran\b|\bawjila\b|\bsorman\b|\bal jawf\b)",
            postinto = 'imagesoflibya',
            getfromthese = {'libya'}
            )
    #louisiana
        swim(r,
            submission = post,
            goodregex = r"(\blouisiana\b)",
            postinto = 'imagesoflouisiana',
            getfromthese = {'louisiana'}
            )
    #maine
        swim(r,
            submission = post,
            goodregex = r"(\bmaine\b)",
            badregex = r"(\bmaine coon\b)",
            postinto = 'imagesofmaine',
            getfromthese = {'maine'}
            )
    #maldives
        swim(r,
            submission = post,
            goodregex = r"(\bmaldives\b|\bmaldivian\b|\bMalé\b|\bHulhumal(é|e)\b|\bmulee-aage\b|\bhulhul(é|e)\b|\bhithadhoo\b|\bvillingili\b|\bmaradhoo\b|\bhulhumeedhoo\b|\bthilafushi\b|\bthilafushi\b|\bmeedhoo\b)",
            postinto = 'imagesofmaldives',
            getfromthese = {'maldives'}
            )
    #maryland
        swim(r,
            submission = post,
            goodregex = r"(\bmaryland\b)",
            postinto = 'imagesofmaryland',
            getfromthese = {'maryland'}
            )
    #Massachusetts
        swim(r,
            submission = post,
            goodregex = r"(\bmassachusetts\b)",
            postinto = 'imagesofmassachusetts',
            getfromthese = {'massachusetts'}
            )
    #Mexico
        swim(r,
            submission = post,
            goodregex = r"(\bmexico\b|\btulum\b|\bchichen itza\b|\bmuseo nacional de antropolog(í|i)a\b|\bchapultepec castle\b|\bcoba\b|\bCanc(ú|u)n\b|\bplaya del carmen\b|\bcabo san lucas\b|\bpuerto vallarta\b)",
            badregex = r"(\bnew mexico\b)",
            postinto = 'imagesofmexico',
            getfromthese = {'mexico', 'fotosmexico'}
            )
    #michigan
        swim(r,
            submission = post,
            goodregex = r"(\bmichigan\b)",
            postinto = 'imagesofmichigan',
            getfromthese = {'michigan'}
            )
    #minnesota
        swim(r,
            submission = post,
            goodregex = r"(\bminnesota\b)",
            postinto = 'imagesofminnesota',
            getfromthese = {'minnesota'}
            )
    #mississippi
        swim(r,
            submission = post,
            goodregex = r"(\bmississippi\b)",
            badregex = r"(\bmississippi river\b)",
            postinto = 'imagesofmississippi',
            getfromthese = {'mississippi'}
            )
    #missouri
        swim(r,
            submission = post,
            goodregex = r"(\bmissouri\b)",
            postinto = 'imagesofmissouri',
            getfromthese = {'missouri'}
            )
    #montana
        swim(r,
            submission = post,
            goodregex = r"(\bmontana\b|\bMT\b|\bglacier national park\b|\bbozeman\b|\bwhitefish\b|\bgreat falls\b|\bmissoula\b|\bwest yellowstone\b|\bkalispell\b|\bhelena\b|\bbig sky\b|\blittle bighorn battlefield\b|\bgardiner\b|\blivingston\b|\bflathead lake\b|\bwest glacier\b|\bbutte\b|\bred lodge\b|\bvirginia city\b|\bhavre\b|\bpolson\b|\bcolumbia falls\b|\bgiant springs state park\b|\banaconda\b|\bmiles city\b|\bglendive\b|\blewistown\b|\bcooke city\b|\bsilver gate\b|\bthompson falls\b|\bbigfork\b|\blake mcdonald\b|\bwild horse island\b|\beast glacier park\b|\bfort benton\b|\bthree forks\b|\bgrinnell glacier\b|\blogan pass\b|\bhungry horse\b|\bmonarch\b|\bgallatin gateway\b|\bdeer lodge\b|\bdillon\b|\bforsyth\b|\bhardin\b|\bcut bank\b|\bhot springs\b|\bbig timber\b)",
            badregex = r"(\b(hannah|joe|tony) montana\b|\bmaine\b|\bsan diego\b|\bgarrett hardin\b|\btexas\b|\btx\b|\bar\b|\barkansas\b|\bmontana de oro\b|\bmt-|\bnikulina\b|\bhelena soares\b|\bco\b|\bcolorado\b|\bcrested butte\b|\b(academy's|the|nammor|air|kvd) monarch\b|\bmonarch (bars|rhapsody)\b|\banaconda vice\b|\ble havre\b|\bpc mt\b|\bcolorado\b|\b(by|from|julie|matt) dillon\b|\bdillon (danis|thomas|fancis)\b|\blake whitefish\b|\bjonathan livingston\b|\bbruce forsyth|\bvirginia\b|\bmaryland\b|\bmd\b)",
            badcaseregex = r"(\bMt\b|\bmt\b|\bmT\b|\bME\b|\banaconda\b|\bmonarch\b|\bCO\b|\bbutte\b|\bVA\b)",
            smallsubredditblacklist = {'arkansas', 'yugioh', 'silverbugs', 'elitedangerous', 'flytying', 'washingtondc', 'nova', 'sneks'},
            postinto = 'imagesofmontana',
            getfromthese = {'montana'}
            )
    #nebraska
        swim(r,
            submission = post,
            goodregex = r"(\bnebraska\b)",
            postinto = 'imagesofnebraska',
            getfromthese = {'nebraska'}
            )
    #netherlands
        swim(r,
            submission = post,
            goodregex = r"(\bnetherlands\b|\bamsterdam\b|\brotterdam\b|\bhague\b|\bmaastricht\b|\butrecht\b|\brijksmuseum\b|\banne frank house\b|\bkeukenhof\b|\bvondelpark\b|\bmadurodam\b)",
            badregex = r"(\bnew york\b|\bNY\b)",
            postinto = 'imagesofnetherlands',
            getfromthese = {'netherlands', 'thenetherlands', 'netherlandspics'}
            )
    #nevada
        swim(r,
           submission = post,
            goodregex = r"(\bnevada\b)",
            postinto = 'imagesofnevada',
            getfromthese = {'nevada'}
            )
    #new hampshire
        swim(r,
            submission = post,
            goodregex = r"(\bnew hampshire\b)",
            postinto = 'imagesofnewhampshire',
            getfromthese = {'newhampshire'}
            )
    #new jersey
        swim(r,
            submission = post,
            goodregex = r"(\bnew jersey\b)",
            badcaseregex = r"(\bnew jersey\b|\bNew jersey\b|\bnew Jersey\b)",
            postinto = 'imagesofnewjersey',
            getfromthese = {'newjersey'}
            )
    #new mexico
        swim(r,
            submission = post,
            goodregex = r"(\bnew mexico\b|\bsanta fe\b|\balbuquerque\b|\broswell\b|\btaos\b|\bcarlsbad\b|\bruidoso\b|\blas cruces\b|\bwhite sands\b|\blos alamos\b|\balamogordo\b|\bcarlsbad\b|\bchaco culture\b|\btucumcari\b|\bbandelier\b|\bsilver city\b|\bred river\b|\bfarmington\b|\bsanta rosa\b|\bdeming\b|\bacoma pueblo\b|\blordsburg\b|\bangel fire\b|\bclayton\b|\bTruth or consequences\b|\bEspa(n|ñ)ola\b|\bzuni\b|\bclovis\b|\bmesilla\b|\bartesia\b|\bsocorro\b|\beagle nest lake\b|\bportales\b|\bAbiqui(ú|u)\b|\bshiprock\b|\btaos pueblo\b|\btaos ski valley\b|\bcity of rocks\b|\bchama\b|\belephant butte\b)",
            badregex = r"(\bminnesota\b|\bclayton bigsby\bfilipe albuquerque\b|\bred river gorge\b|\bkentucky\b|\bky\b)",
            badcaseregex = r"(\bchama\b|\bsspa(n|ñ)ola\b)",
            smallsubredditblacklist = {'atlanta'},
            postinto = 'imagesofnewmexico',
            getfromthese = {'newmexico', 'albuquerque', 'unm', 'lascruces', 'nmsu', 'santafe', 'carlsbadnm'}
            )
    #new york
        swim(r,
            submission = post,
            goodregex = r"(\bnew york\b|\bNYC?\b|\blong island\b|\balbany\b|\bthousand islands\b|\bfinger lakes\b|\brochester\b|\bsyracuse\b|\blake placid\b|\bithaca\b|\blake george\b|\bbinghampton\b|\bmontauk\b|\bplattsburgh\b|\bwoodstock\b|\bpoughkeepsie\b|\bwoodbury\b|\bnew paltz\b|\bbethel\b|\bsaratoga springs\b|\bwatkins glen\b|\balexandria bay\b|\bwest point\b|\bsleepy hollow\b|\belmira\b|\brhinebeck\b|\btarrytown\b|\bcooperstown\b|\bellicottville\b|\bfire island\b|\bcold spring\b|\bbear (mountain|mt)\b|\butica\b|\bcorning\b|\bwhite plains\b|\bp(or)?t chester\b|\bshelter island\b|\bcayuga lake\b|\bletchworth state park\b|\bhyde park\b|\bwatertown\b|\bamityville\b|\bwestbury\b|\bmargaret lewis norrie state park\b|\bogdensburg\b|\bport jefferson\b)",
            smallsubredditblacklist = {'austin'},
            postinto = 'imagesofnewyork',
            getfromthese = {'newyork', 'nyc', 'nycpics', 'nycstreetart', 'nychistory'}
            )
    #new zealand
        swim(r,
            submission = post,
            goodregex = r"(\bnew zealand\b|\bauckland\b|\bqueenstown\b|\bchristchurch\b|\bwellington\b|\brotorua\b|\bdunedin\b|\btaupo\b|\bnelson\b|\bnapier\b|\bhawke's bay\b|\bwanaka\b|\bbay of islands\b|\bmarlborough\b|\blake tekapo\b|\bkaikoura\b|\bpicton\b|\bte anau\b|\bblenheim\b|\bfox glacier\b|\bpaihai\b|\btauranga\b|\bcoromandel\b|\bcoromandel\b|\bakaroa\b|\babel tasman\b|\bgreymouth\b|\bhanmer springs\b|\bgrisborne\b|\bcape reinga\b|\bwaitomo\b|\binvercargill\b|\bnew plymouth\b|\bpalmerston north\b|\blake wanaka\b|\btimaru\b|\bwhanganui\b|\bthames\b|\bashburton\b|\bstewart island\b|\bhokitika\b|\boamaru\b|\bmatamata\b|\bwarkworth\b|\barrowtown\b|\bcromwell\b|\bwakatipu\b|\bwestport\b|\bmilford sound\b|\bsky tower\b|\blake taupo\b|\bbay of islands\b|\blake wanaka\b|\btongariro\b|\bFiordland\bwaiotapu\b|\bhuka falls\b|\babel tasman\b|\bwaitomo\b|\bdoubtful sound\b|\bToit(u|ū) Otago\b|\bkelly tarlton's sea life aquarium\b|\broutebum track\b|\bfox glacier\b|\bpukekura\b|\binternational antarctic centre\b|\brangitoto\b|\bmilford track\b|\botago peninsula\b|\bhot water beach\b|\bwakatipu\b|\bte whanganui-a-hei\b|\baoraki\b|\bmount cook\b|\bzealandia\b|\bchristchurch\b|\bwaiheke\b|\bwaimangu\b|\bkepler track\b|\bmount maunganui\b|\borana wildlife park\b|\bwillowbank wildlife reserve\b|\bwaitomo glowworm caves\b|\bwellington botanic garden\b|\bwaitemata harbour\b|\blake te anau\b|\bhamilton gardens\b|\bwestland tai poutini\b|\bwellington museum\b|\bkauri museum\b|\bwhanganui\b)",
            badregex = r"(\b(george|willie\reggie|jj|major) nelson\b|\b(beef|pork) wellington\b|\bnelson mandela\b|\bpoland\b|\bwroclaw\b|\bkaohsiung\b|\btaiwan\b|\briver thames\b|\bthames river|\blondon\b|\bunited kingdom\b)",
            smallsubredditblacklist = {'eliteracers'},
            postinto = 'imagesofnewzealand',
            getfromthese = {'newzealand', 'newzealandpics', 'nzphotos', 'nzmetahub', 'nzdepthhub', 'nzcirclejerk', 'winstonjerk', 'srsnz', 'nzsubredditdrama', 'nzsubredditdramadrama', 'nzmodmaildrama', 'meta_new_zealand', 'nzsecretsquirrel', 'nzcirclejerkcopypasta', 'nzfightclub', 'truenewzealand', 'truezealand', 'truenz', 'newzealand', 'new_zealand', 'nuzilland', 'aotearoa', 'auckland', 'wellington', 'christchurch', 'chch', 'thetron', 'universityofauckland', 'hawkesbay', 'dunedin', 'nelsonnz', 'taranaki', 'palmy', 'palmerstonnorth', 'bayofplenty', 'blenheim', 'queenstown', 'rangiora', 'greylynn', 'arovalley', 'newtownrulz', 'vuw', 'mtalbert', 'eit', 'marton_nz', 'stewartisland', 'nzfood', 'kiwicaching', 'kokako', 'newzealandproblems', 'nzmigrants', 'nzbeer', 'thatpicofnzfromspace', 'newzealandhistory', 'nzmalefashionadvice', 'nzatheism', 'percapitabragging', 'nzcringe', 'nzforsale', 'nzphotos', 'kiwitech', 'nzmemes', 'nzlgbt', 'nzredditisland', 'rcnz', 'ketonz', 'nzknittingandcrochet', 'nzwizards', 'destinychurch', 'wellingtonhaircuts', 'nowellingtonhaircuts', 'nuzilland', 'nzindoors', 'nzconfessions', 'nzbitcoin', 'cryptokiwis', 'nzmusic', 'nzmusicians', 'newzealandmusic', 'kiwirock', 'nzreggae', 'hiphopnz', 'newzealandfilm', 'nzfilm', 'nzmovies', 'gcsbbill', 'notthecivilian', 'nzpolitics', 'nzgreen', 'nzsucks', 'occupynz', 'nznews', 'newzealandparliament', 'nztrees', 'nztreeschch', 'nzgaming', 'nzesg', 'nztf2', 'lolnewzealand', 'kiwilol', 'minecraftnz', 'nztikitour', 'nztravel', 'askakiwi', 'holidaynewzealand', 'nzgonewild', 'nzcreepshots', 'nzfootball', 'nzsports', 'aleague', '4wdnz', 'nzoutdoors', 'nztv', 'theridges', 'shortlandstreet', 'thealmightyjohnson'}
            )
    #north carolina
        swim(r,
            submission = post,
            goodregex = r"(\bnorth carolina\b)",
            postinto = 'imagesofnorthcarolina',
            getfromthese = {'northcarolina'}
            )
    #north dakota
        swim(r,
            submission = post,
            goodregex = r"(\bnorth dakota\b)",
            badregex = r"(\bnorthdakota\b)",
            postinto = 'imagesofnorthdakota',
            getfromthese = {'northdakota'}
            )
    #norway
        swim(r,
            submission = post,
            goodregex = r"(\bnorway\b)",
            postinto = 'imagesofnorway',
            getfromthese = {'norwaypics', 'norway', 'norwayonreddit'}
            )
    #ohio
        swim(r,
            submission = post,
            goodregex = r"(\bohio\b)",
            postinto = 'imagesofohio',
            getfromthese = {'ohio'}
            )
    #oklahoma
        swim(r,
            submission = post,
            goodregex = r"(\boklahoma\b)",
            postinto = 'imagesofoklahoma',
            getfromthese = {'oklahoma'}
            )
    #oregon
        swim(r,
            submission = post,
            goodregex = r"(\boregon\b)",
            badregex = r"(\bMcCarthy(’s)? Oregon\b)",
            postinto = 'imagesoforegon',
            getfromthese = {'oregon'}
            )
    #pennsylvania
        swim(r,
            submission = post,
            goodregex = r"(\bpennsylvania\b)",
            postinto = 'imagesofpennsylvania',
            getfromthese = {'pennsylvania'}
            )
    #peru
        swim(r,
            submission = post,
            goodregex = r"(\bperu\b|\blima\b|\bcusco\b|\barequipa\b|\biquitos\b|\bpuno\b|\bcolca canyon\b|\bMan(ú|u) National Park\b|\bhuaraz\b|\bmachu picchu\b|\bsacred valley\b|\bsaksaywaman\b|\bqurikancha\b|\bUrubamba\b|\bsanta catalina monastery\b|\bhuayna picchu\b|\bhuaca pucllana\b)",
            badregex = r"(\blima bean\b|\bAdriana Lima\b)",
            postinto = 'imagesofperu',
            getfromthese = {'peru', 'perupics'}
            )
    #rhode island
        swim(r,
            submission = post,
            goodregex = r"(\brhode island\b)",
            postinto = 'imagesofrhodeisland',
            getfromthese = {'rhodeisland'}
            )
    #russia
        swim(r,
            submission = post,
            goodregex = r"(\brussian?\b|\bmoscow\b|\bsaint petersburg\b|\blake baikal\b|\bsochi\b|\bvladivostok\b|\bkaliningrad\b|\bvolgograd\b|\birkutsk\b|\bkazan\b|\bmurmansk\b|\bkhabarovsk\b|\bsamara\b|\byekaterinburg\b|\bsakhalin\b|\bnovosibirsk\b|\byakutsk\b|\bveliky novgorod\b|\bkrasnoyarsk\b|\bgrozny\b|\bomsk\b|\bnizhny novgorod\b|\bsuzdal\b|\bsolovetsky islands?\b|\bufa\b|\bmagadan\b|\brostov\bon\bdon\b|\bkrasnodar\b|\btomsk\b|\bulan\bude\b|\bnorilsk\b|\bchelyabinsk\b|\bolkhon island\b|\bpetropavlovsk\bkamchatsky\b|\byuzhno\bsakhalinsk\b|\byaroslavl\b|\bpetro\b|\bsaratov\b|\bvoronezh\b|\btula\b|\btver\b|\btyumen\b|\bizhevsk\b|\bgelendzhik\b|\bnakhodka\b|\boymyakon\b|\btolyatti\b)",
            postinto = 'imagesofrussia',
            getfromthese = {'russia', 'russiapics'}
            )
    #scotland
        swim(r,
            submission = post,
            goodregex = r"(\bscotland\b|\bedinburgh\b|\bglasgow\b|\bloch ness\b|\bskye\b|\bscottish highlands\b|\bdundee\b|\bislay\b|\baviemore\b|\bloch lomond\b|\bpitlochry\b|\bcallander\b|\bgretna green\b|\binveraray\b|\bballater\b|\bmelrose\b|\bdrunkeld\b|\bbraemar\b|\bleith\b|\baberfoyle\b|\bfalkirk\b|\bbarra\b|\bkillin\b|\bcairngorms\b|\bdrumnadrochit\b|\bpeebles\b|\bgrantown-on-spey\b|\binverurie\b|\bfort augustus\b|\bluss\b|\baberfeldy\b|\bnewtonmore\b|\bcrieff\b|\bcastle douglas\b|\bstrathpeffer\b|\bballoch\b|\blewis and harris\b|\bauchterarder\b|\bballachulish\b|\brothesay\b|\bedinburgh\b|\bholyrood\b|\bkelvingrove\b|\barthur's seat\b|\bglasgow\b|\bprinces st(reet)?\b|\bburrell collection\b|\bs(ain)?t gile'?s cathedral\b|\bfalkirk wheel\b|\bmary king'?s close\b|\burquhart\b|\bmelrose abbey\b|\bkelvingrove park\b|\bcairngorms\b|\bblair drummond safari\b|\bour dynamic earth\b|\bhunterian museum\b|\bmcmanus galleries\b|\bwallace monument\b|\briverside museum\b|\bculzean castle\b|\bs(ain)?t andrews cathedral\b|\bfalkland palace\b|\bbroughty castle\b|\bbalmoral castle\b|\brosslyn chapel\b|\bgleneagles hotel\b|\bskara brae\b|\bglamis castle\b|\bsse hydro\b)",
            postinto = 'imagesofscotland',
            getfromthese = {'scotland', 'scottishphotos'}
            )
    #south carolina
        swim(r,
            submission = post,
            goodregex = r"(\bsouth carolina\b)",
            badregex = r"(\bwv\b|\bwest virginia\b)",
            postinto = 'imagesofsouthcarolina',
            getfromthese = {'southcarolina', 'aiken', 'columbiyeah', 'florencesc', 'georgetownsc', 'greenwoodsc', 'greenville', 'hiltonhead', 'myrtlebeach', 'newberry', 'powdersville', 'rockhill', 'simpsonville', 'spartanburg', 'easley', 'andersonsc', 'sumter', 'unionsc', 'westminstersc', 'charleston'}
            )
    #south dakota
        swim(r,
            submission = post,
            goodregex = r"(\bsouth dakota\b)",
            postinto = 'imagesofsouthdakota',
            getfromthese = {'southdakota'}
            )
    #syria
        swim(r,
            submission = post,
            goodregex = r"(\bsyria\b|\bdamascus\b|\baleppo\b|\blattakia\b|\bpalmyra\b|\btartus\b|\bkilis\b|\bkessab\b|\bal-raqqah\b|\bal-zabadani\b|\bhoms\b|\bas-suwayda\b|\bbaniyas\b|\bhama\b|\bmasyaf\b|\bmarmarita\b|\bbosra\b|\bmajdal shams\b|\bsafita\b|\bnimrod fortress\b|\bayn al-arab\b|\bmal'loula\b|\bdaraa\b|\bdeir ez-zor\b|\bafrin\b|\bidlib\b|\bal-hasakah\b|\bsaidnaya\b|\bal-qamishli\b|\bsayyidah zaynab\b|\bsalah ed-din\b|\blake assad\b|\bjaramana\b|\bjableh\b|\byabroud\b|\bharasta\b|\bras al-ayn\b|\bal-hasakah governorate\b|\bmashta al-helu\b|\blake homs\b|\byaafour\b)",
            badregex = r"(\bdamascus steel\b)",
            smallsubredditblacklist = {'knifemaking', 'knifeclub', 'knives', 'knifeporn', 'bladesmith'},
            postinto = 'imagesofsyria',
            getfromthese = {'syria', 'syriancivilwar'}
            )
    #tennessee
        swim(r,
            submission = post,
            goodregex = r"(\btennessee\b)",
            postinto = 'imagesoftennessee',
            getfromthese = {'tennessee'}
            )
    #terlingua
        swim(r,
            submission = post,
            goodregex = r"(\bterlingua\b)",
            postinto = 'terlingua',
            getfromthese = {'null'}
            )
    #texas
        swim(r,
            submission = post,
            goodregex = r"(\btexas\b|\btx\b|\btexans?\b|\baustin\b|\bdallas\b|\bhouston\b|\bsan antonio\b|\bfo?r?t worth\b|\bel paso\b|\barlington\b|\bcorpus christi\b|\bplano\b|\blaredo\b)",
            badregex = r"(\baustin (powers|seven)\b|\b(blake|lana|steve|jane|terry) austin\b|\balexis texas\b|\bbryce dallas\b|\barlington national cemetery\b|\bdallas keuchel\b|\bvirginia\b|\bva\b|\bnova\b|\bdevin houston\b)",
            smallsubredditblacklist = {'nova', 'virginia'},
            postinto = 'imagesoftexas',
            getfromthese = {'lonestar', 'texas', 'texasbeer', 'texaschl', 'texas_classifieds', 'texasfavors', 'texascountry', 'texasguns', 'texashistory', 'texashistoryporn', 'texents', 'txmoto', 'texaspolitics', 'texas_reddirt', 'texasskateboarding', 'truetexas', 'abilenetexas', 'abilene', 'allen', 'amarillo', 'aransaspass', 'arlington', 'arlingtontx', 'atascocitatx', 'atascocita', 'austin', 'austintexas', 'askaustin', 'fireteamaustin', 'austinbeer', 'bitcoinaustin', 'austinbloggers', 'austincarpangler', 'austincirclejerk', 'austinclassifieds', 'austinclimbing', 'austincomedy', 'bikingatx', 'depressionaustin', 'austindiscgolf', 'austindogs', 'eastsidechess', 'effaustin', 'austinevents', 'austinfilmmakers', 'austinfood', 'austinfrugal', 'atxgaybros', 'austingaymers', 'austingonewild', 'atxgooglefiber', 'austingreenbelt', 'austinguns', 'helpmeaustin', 'austinintrovertsocial', 'austinjeeps', 'austinjobs', 'austinkids', 'austinliving', 'keepaustinweird', 'atxlostandfound', 'austinmtg', 'austincannabis', 'austents', 'austinents', 'austintrees', 'austin_metal', 'austinmotorcycles', 'atxmusic', 'austintxmusic', 'livemusiccapital', 'austinshowlistings', 'austinmusicians', 'austinbiz', 'pedicabatx', 'austinpetlostandfound', 'atxpix', 'austinphotography', 'austinpoker', 'queeraustin', 'atx4atx', 'austinrecsandreviews', 'atxrecords', 'atxrecsports', 'rentaustin', 'restorethefourthatx', 'austinrp', 'austinrunning', 'austinscience', 'austinshows', 'socialanxietyaustin', 'barcraftaustin', 'austinstartups', 'austinswap', 'austintrades', 'austintraffic', 'austinurbex', 'austinveg', 'austinyoga', 'occupyaustin', 'semisaltyeggsinaustin', 'trueaustin', 'bastroptx', 'baycitytx', 'baytown', 'belton', 'benbrook', 'boerne', 'boyd', 'brownwood_texas', 'carrolltontx', 'castroville', 'cedarcreek', 'cedarpark', 'clearlake', 'collegestation', 'collegestationbeer', 'commercetx', 'conroe', 'copperascove', 'corpus', 'corpuschristi', 'corsicanatx', 'cypresstx', 'dallas', 'dallasfood', 'dallasmeetups', 'dallasriders', 'deerpark', 'denton', 'truedenton', 'drippingsprings', 'edinburg', 'elpaso', 'elpasobeer', 'euless', 'flowermound', 'forney', 'fortbend', 'fortworth', 'friendswood', 'frisco', 'fulshear', 'galveston', 'garland', 'georgetowntx', 'granbury', 'gptx', 'greenvilletx', 'heartland', 'heidenheimer', 'highlandvillage', 'houston', 'houstonbeer', 'houstonclassifieds', 'bikehouston', 'houstonevents', 'houstonfood', 'houstonguns', 'houstonjob', 'houstonents', 'houstonsocials', 'houstonriders', 'houstonmusic', 'houstonr4r', 'houstonsocials', 'houstonsoccer', 'huntsvilletx', 'huntsvilletexas', 'hurst', 'irvingtexas', 'jerseyvillage', 'jollyville', 'katytx', 'katy_texas', 'katy', 'keller', 'kerrville', 'killeen', 'kingwood', 'laredo', 'cityoflaredo', 'leander', 'lewisville', 'lockhart', 'longviewtexas', 'lubbock', 'lubbocktx', 'lubbockdogs', 'lubbockmusicians', 'marblefalls', 'marfa', 'manor', 'mckinney', 'mineralwells', 'newbraunfels', 'oakcliff', 'palestinetx', 'paristx', 'paristexas', 'pearland', 'pflugerville', 'plano', 'planotx', 'portaransas', 'richardson', 'riveroaks', 'rockwall', 'roundrock', 'roundrocktexas', 'san_angelo', 'sanantonio', 'bikesanantonio', 'sanantoniofood', 'satx4satx', 'sanmarcos', 'sanger', 'springbranch', 'sugarland', 'stephenville', 'terlingua', 'texarkana', 'thecolony', 'thewoodlands', 'tomball', 'tylertx', 'wichitafalls', 'waco', 'weatherford', 'whitesettlement', 'wimberley', 'austinsanantonio', 'bigbend', 'bigbendtx', 'bigbendnationalpark', 'brazoriacounty', 'bcstx', 'dfw', 'dfwart', 'dfwbeer', 'dfwclassifieds', 'dallist', 'dfwbike', 'dfwfilmmakers', 'dfwgaming', 'dfwgameswap', 'dfwgaymers', 'dfwguns', 'dfwjobs', 'dfwmarketplace', 'dfwmusic', 'dfwpets', 'r4rdfw', 'dfwroommates', 'gasmonkey', 'theticket', 'east_texas', 'easttexas', 'easttx', 'hillcountry', 'laketravis', 'leandercedarpark', 'midessa', 'northtexas', 'nwatx', 'riograndevalley', 'audirgv', 'gayrgv', 'rgvstandup', 'southtexas', 'setx', 'setxmusic', 'valley956', 'westcentraltexas', 'westtexas', 'wilcocorruption', 'alamocolleges', 'acu', 'austinisd', 'atxcommcollege', 'austincc', 'baylor', 'boydhighschool', 'collincollege', 'lamaruniversity', 'northwestvista', 'riceuniversity', 'shsu', 'smu', 'sasaustin', 'stedwards', 'stmu', 'aggies', 'tamuc', 'tcu', 'tccstudentsconnect', 'txstate', 'tstcharlingen', 'texassouthern', 'texastech', 'trinityu', 'universityofhouston', 'uhd', 'uhlc', 'coogshouse', 'unt', 'stthomas', 'universityoftexas', 'utarlington', 'uttrees', 'utmemes', 'longhorn', 'universityoftexas', 'utaustin', 'shadownet', 'utbrownsville', 'utdallas', 'utep', 'utsa', 'longhornnation', 'uiw', 'wtamu', 'cowboys', 'mavericks', 'dallasstars', 'fcdallas', 'astros', 'dynamo', 'rockets', 'texans', 'texansff', 'roundrockexpress', 'sascorpionsfc', 'nbaspurs', 'texasrangers', 'txrangersexpress', '12thmanfootball', 'longhornnation', 'aclfestival', 'austincitylimits', 'funfunfunfest', 'txrenaissancefestival', 'sxsw', 'sxswi'}
            )
    #toronto
        swim(r,
            submission = post,
            goodregex = r"(\btoronto\b)",
            postinto = 'imagesoftoronto',
            getfromthese = {'toronto', 'UofT', 'Ryerson', 'YorkU', 'Humber', 'Brampton', 'GeorgeBrownCollege', 'TorontoBiking', 'TOmaps', 'TOFoodie', 'FoodToronto', 'TOtrees', 'TorontoArt', 'FishingOntario', 'TorontoCraftBeer', 'TorontoParks', 'TorontoUrbanFishing', 'Leafs', 'TorontoBlueJays', 'TorontoRaptors', 'TFC', 'TorontoRenting', 'TorontoRealEstate', 'TorontoJobs', 'VolunteerToronto', 'TorontoTransit', 'TorontoCityHall', 'FrugalTO', 'TorontoDriving'}
            )
    #usa
        swim(r,
            submission = post,
            goodregex = r"(\busa\b|\bamerican?s?\b|\bmurica\b|\bunited states\b)",
            badregex = r"((north|central|south|captain) (america|murica)|\bamerican cheese\b)",
            postinto = 'imagesofusa',
            getfromthese = {'unitedstatesofamerica'}
            )
    #utah
        swim(r,
            submission = post,
            goodregex = r"(\butah\b)",
            postinto = 'imagesofutah',
            getfromthese = {'utah'}
            )
    #vermont
        swim(r,
            submission = post,
            goodregex = r"(\bvermont\b)",
            postinto = 'imagesofvermont',
            getfromthese = {'vermont'}
            )
    #virginia
        swim(r,
            submission = post,
            goodregex = r"(\bvirginia\b)",
            badregex = r"(\bwest virginia\b)",
            postinto = 'imagesofvirginia',
            getfromthese = {'virginia'}
            )
    #wales
        swim(r,
            submission = post,
            goodregex = r"(\bwales\b|\bconwy castle\b|\bbodnant garden\b|\bbig pit national coal museum\b|\bsnowdon\b|\bllechwedd slate caverns\b|\bcastell coch\b|\bdan yr ogof\b|\bsnowdon mountain railway\b|\bnational slate museum\b|\bnational roman legion museum\b|\bpontcysyllte aqueduct\b|\bpowis castle\b|\bpembroke castle\b|\boakwood theme park\b|\bpen y fan\b|\bdinorwig power station\b|\btredegar house\b|\bsyngun copper mine\b|\bdinefwr castle\b|\bharlech castle\b|\bceltic manor resort\b|\b cadair idris\b|\btryfan\b|\bcrib goch\b|\bllangollen canal\b|\bcoed-y-brenin\b|\bmoel famau\b|\bchirk castle\b|\bpen-y-pass\b|\bglyder fawr\b|\bmonmouthshire\b|\bpistyll raeadr\b|\bwhitesands bay\b|\bgrand theatre\b|\bgoodrich castle\b|\bllangollen railway\b|\bpuzzlewood\b|\bclearwell caves\b|\bsgwd henrhyd\b|\bblue lagoon waterpark\b|\bswallow falls\b|\bglyder fach\b|\berddig\b|\bhorseshoe pass\b|\blc swansea\b|\bdyffryn gardens\b|\bllanberis lake railway\b|\bcastell dinas br(a|â)n\b|\bswansea\b|\bbrecon\b|\bpembrokeshire\b|\bbridgend\b|\bllangollen\b|\bbetws-y-coed\b|\bwrexham\b|\bbala\b|\bmonmouth\b|\bllanberis\b|\bportmeirion\b|\bdolgellau\b|\bdardigan\b|\babergavenny\b|\bblaenau ffestiniog\b|\bblack mountains\b|\bbeddgelert\b|\bharlech\b|\bwelshpool\b|\bcaerphilly\b|\bllandovery\b|\bcrickhowell\b|\bmachynlleth\b|\bllanfairpwllgwyngyll\b|\bruthin\b|\bskomer\b|\bllangors\b|\bffestiniog\b|\bst clears\b|\bmerthyr tydfil\b|\bebbw vale\b|\bpontypridd\b|\baberdare\b|\bpendine\b|\bllandeilo\b|\brhossili\b|\bllandrindod wells\b|\bcapel curig\b|\bnarberth\b|\bllanbedr\b|\bblaenavon\b|\bystradgynlais\b|\btreforest\b|\baberdaron\b|\brisca\b|\bpontypool\b)",
            badregex = r"(\bblackpool\b|\blancashire\b|\bengland\b)",
            postinto = 'imagesofwales',
            getfromthese = {'wales'}
            )
    #washington
        swim(r,
            submission = post,
            goodregex = r"(\bwashington\b)",
            badregex = r"(\bd\.?c\.?\b|\bgeorge washington\b|\bdenzel washington\b|\bil\b|\billinois\b|\bwashington monument\b|\bwashington post\b)",
            postinto = 'imagesofwashington',
            getfromthese = {'washington', 'mount_rainier'}
            )
    #washingtondc
        swim(r,
            submission = post,
            goodregex = r"(\bwashington dc\b|\bdistrict of columbia\b|\bwhite house\b|\bnational mall\b|\bunites states capitol\b|\blincoln memorial\b|\bnational museum of natural history\b|\bnational zoological park\b|\bnational air and space museum\b|\bvietnam veterans memorial\b|\bwashington monument\b|\bthomas jefferson memorial\b|\bunited states holocaust memorial\b|\binternational spy museum\b|\bnational world war ii memorial\b|\bnewseum\b|\bsmithsonian\b|\bwashington national cathedral\b|\bford's theatre\b|\bkorean war veterans memorial\b|\bjohn f\.? kennedy center for the performing arts\b|\bfranklin delano roosevelt memorial\b|\bunited states botanic garden\b|\bmadame tussauds washington\b|\bnational portrait gallery\b|\bnational archives\b|\bnational building museum\b|\bhirshhorn museum and sculpture\b|\bthe phillips collection\b|\bunited states national arboretum\b|\bnational museum of african art\b|\bnational museum of crime\b|\bnational postal museum\b|\brenwick gallery\b|\bhillwood estate\b|\bbasilica of the national shrine of the immaculate conception\b|\bfreer gallery of art\b|\bcorcoran gallery of art\b|\banacostia community museum\b|\bunited states capitol visitor center\b|\barts and industries building\b|\btudor place\b|\barthur m\.? sackler gallery\b|\bfolger shakespeare library\b|\borganization of american states\b|\b9:30 club\b|\bnational academy of sciences\b)",
            badregex = r"(\bpolish national archives\b)",
            postinto = 'imagesofwashingtondc',
            getfromthese = {'washingtondc', 'dcphotography'}
            )
    #west virginia
        swim(r,
            submission = post,
            goodregex = r"(\bwest virginia\b|\bw virginia\b|\bWV\b|pipestem resort\b|\bcharleston\b|\bmorgantown\b|\bharpers ferry\b|\bcoopers rock state forest\b|\bhuntington\b|\bnew river gorge\b|\bcanaan valley\b|\bwhite sulphur springs\b|\belkins\b|\bsnowshoe\b|\bfayetteville\b|\bmoundsville\b|\bblackwater falls\b|\bwheeling\b|\boak hill\b|\bseneca rocks\b|\bcharles town\b|\bcass\b|\bparkersburg\b|\bfairmont\b|\bblennerhassett island\b|\blewisburg\b|\bbeckley\b|\bwilliamstown\b|\bnorth bend state park\b|\bgreenbrier river trail\b|\bbabcock\b|\bbridgeport\b|\bharpers ferry national historical park\b|\bmartinsburg\b|\bbuckhannon\b|\bclarksburg\b|\bcamp creek state park\b|\bwatoga state park\b|\bbluefield\b|\bbramwell\b|\blost river\b|\bpoint pleasant\b|\broanoke\b|\bshepherdstown\b|\bmonongahela\b|\bbarboursville\b|\bmarlinton\b)",
            badregex = r"(\brosie huntington.whiteley\b|\bsc\b|\bsouth carolina\b|\bhart and huntington\b)",
            badcaseregex = r"(\bwheeling\b)",
            smallsubredditblacklist = {'charleston', 'hdm_stuttgart', '4x4'},
            postinto = 'imagesofwestvirginia',
            getfromthese = {'westvirginia'}
            )
    #wisconsin
        swim(r,
            submission = post,
            goodregex = r"(\bwisconsin\b)",
            postinto = 'imagesofwisconsin',
            getfromthese = {'wisconsin'}
            )
    #wyoming
        swim(r,
            submission = post,
            goodregex = r"(\bwyoming\b\|\bwy\b|\byellowstone\b|\bgrand teton\b|\blaramie\b|\bteton village\b|\bjackson lake\b|\brawlins\b|\brock springs\b|\bdevils tower\b|\bthermopolis\b|\bmoran\b|\bevanston\b|\bjenny lake\b|\bboysen reservoir\b|\blander\b|\briverton\b|\bcolter bay\b|\bglendo state park\b|\bgreen river\b|\bdubois\b|\btorrington\b|\bsignal (mountain|mtn)\b|\bguernsey state park\b|\blusk\b|\bgreybull\b|\bsaratoga\b|\bkeyhole state park\b|\bworland\b|\bsinks canyon\b|\bshoshoni\b|\bpine bluffs\b|\bbighorn national forest\b|\bguernsey\b|\bpinedale\b|\bnewcastle\b|\bold faithful\b)",
            badregex = r"(\bnewcastle united\b|\bbailiwick of guernsey\b|\blander probe\b)",
            postinto = 'imagesofwyoming',
            getfromthese = {'wyoming'}
            )
    #yemen
        swim(r,
            submission = post,
            goodregex = r"(\byemen\b|\bYemenis?\b|\bSocotra\b|\bSana'a\b|\baden\b|\bShibam\b|\bAl Hudaydah\b|\bGhumdan Palace\b|\bCisterns of Tawila\b|\bSheba Palace\b)",
            postinto = 'imagesofyemen',
            getfromthese = {'yemen', 'yemenpics', 'yemenicrisis'},
            )

#gets the OP's account age in days for use in criteria
def getage(r, author):
    print("Getting age")
    user = r.get_redditor(author)
    print(user.created_utc)
    user_date = datetime.utcfromtimestamp(user.created_utc)
    print("{} was born on {}".format(author, user_date))
    age = (datetime.utcnow() - user_date).days
    print("They are {} days old".format(age))
    return age

#defines how critera get applied to each post 
def swim(r, goodregex, postinto, getfromthese, submission, badregex=r"(\bbadregex\b)", badcaseregex=r"(\bBadCaseRegex\b)", smallsubredditblacklist={'blacklistedsubreddit'}):
        title = submission.title
        if (submission.over_18  or
                submission.author.name.lower() in globaluserblacklist or
                not (re.search(domainregex, submission.domain, flags=re.IGNORECASE) or re.search(urlregex, submission.url, flags=re.IGNORECASE))):
            return
        if ((submission.subreddit.display_name.lower() not in globalsubredditblacklist | smallsubredditblacklist and
                re.search(goodregex, title, flags=re.IGNORECASE) and
                not re.search(badregex, title, flags=re.IGNORECASE) and
                not re.search(badcaseregex, title)) or
                submission.subreddit.display_name.lower() in getfromthese):
            age = getage(r, submission.author.name.lower())
            if age > 2:
                make_post(r, submission, postinto)

#makes the post and comment
def make_post(r, originalsubmission, subreddit):
    title = originalsubmission.title
    comment = '[Original post]({}) by /u/{} in /r/{}'.format(originalsubmission.permalink, originalsubmission.author, originalsubmission.subreddit)
    print("Making post in {}: ".format(subreddit))
    print(("    " + title +"\n").encode('utf-8', 'ignore'))
    try:
        xpost = r.submit(subreddit, title, url=originalsubmission.url, captcha=None, send_replies=True)
        xpost.add_comment(comment)
    except praw.errors.AlreadySubmitted as e:
        print("Already submitted. Skipping.\n")
    except praw.errors.APIException as e:
        print(e)
        print("API error. Skipping.")

#defines how to log in using the credentials stored in the OS.
def praw_oauth_login(r):
    
    print('authorizing...')
    
    #Load keys from OS variables
    client_id = os.environ.get("imagesof_client_id")
    print(client_id)
    client_secret = os.environ.get("imagesof_client_secret")
    print(client_secret)
    redirect_uri = "http://127.0.0.1:65010/authorize_callback"
    refresh_token=os.environ.get("imagesof_refresh_token")
    print(refresh_token)
    
    #Set the oauth app info and get authorization
    r.set_oauth_app_info(client_id, client_secret, redirect_uri)
    r.refresh_access_information(refresh_token)
    
    print('...done')

#runs all the things
def main():
    print("Logging in...")

    praw_oauth_login(r)

    while True:
        try:
            search_for_places(r) 
        except praw.errors.HTTPException:
            print("Reddit is down. Sleeping...")
            time.sleep(360)
        except requests.exceptions.ReadTimeout as error:
            print("Handling ReadTimeout: ", error)
        except praw.errors.RateLimitExceeded as e:
            print(("ERROR: Rate limit exceeded. Sleeping for " +
                   "{} seconds".format(e.sleep_time)))
            time.sleep(e.sleep_time)
            

if __name__ == '__main__':
    main()
