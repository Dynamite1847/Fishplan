// 鱼单、清洁队与鱼资料库共用的数据和渲染
const IMG=window.FISH_IMG||{};
// v: ok推荐 opt可选 temp过渡 no不适合；terr守域分0-2；ord入缸先后；grp同类冲突组
const F=[
{id:"clown",cn:"公子小丑（尼莫）",sci:"Amphiprion ocellaris",len:11,cm:"8–11",zone:"中下层",col:"橙底白环黑边",tem:"成对后守地盘",coral:"安全",shrimp:"安全",v:"ok",terr:1,ord:50,grp:"clown",unit:2,liked:1,note:"一对，买人工繁殖、已相处稳定的。黑白色型是同一种，可替换。不保证住进奶嘴。"},
{id:"watch",cn:"黄守望虾虎",sci:"Cryptocentrus cinctus",len:10,cm:"约10",zone:"底层",col:"亮黄，带细蓝点",tem:"温和，守自己洞口",coral:"安全",shrimp:"安全",v:"ok",terr:1,ord:10,grp:"sandgoby",liked:1,note:"趴在砂上打洞，很有表情。可配虎纹枪虾共生。会跳，要盖网。"},
{id:"okin",cn:"黄小丑虾虎",sci:"Gobiodon okinawae",len:3.5,cm:"3.5–4",zone:"停栖",col:"全身柠檬黄",tem:"温和",coral:"基本安全",shrimp:"安全",v:"ok",terr:0,ord:12,grp:"gobiodon",note:"很小，停在石头和珊瑚上，几乎不加负荷，凑数首选。要喂细碎饵。"},
{id:"citr",cn:"柠檬蟋蟀",sci:"Gobiodon citrinus",len:6.5,cm:"约6.5",zone:"停栖",col:"黄色带细蓝线",tem:"温和",coral:"谨慎：可能啄小水螅体硬珊瑚",shrimp:"安全",v:"ok",terr:0,ord:12,grp:"gobiodon",liked:1,note:"软体缸基本没问题。和黄小丑虾虎同类，二选一。"},
{id:"fire",cn:"雷达",sci:"Nemateleotris magnifica",len:8,cm:"7.5–9",zone:"中层",col:"白头红尾，长背鳍",tem:"很温和，胆小",coral:"安全",shrimp:"安全",v:"ok",terr:0,ord:20,grp:"firefish",liked:1,note:"在洞口附近悬停，受惊钻洞。很会跳，必须盖网。只养1条。"},
{id:"deco",cn:"紫雷达",sci:"Nemateleotris decora",len:9,cm:"约9",zone:"中层",col:"淡紫身，紫红鳍",tem:"很温和",coral:"安全",shrimp:"安全",v:"ok",terr:0,ord:20,grp:"firefish",note:"和雷达二选一，颜色更“贵”。同样会跳。"},
{id:"pajama",cn:"睡衣天竺鲷",sci:"Sphaeramia nematoptera",len:9,cm:"8–9",zone:"中层",col:"黄脸红眼，黑带后满身圆点",tem:"很温和",coral:"安全",shrimp:"安全",v:"ok",terr:0,ord:22,grp:"pajama",note:"慢悠悠悬停，长相很特别。可养1–2条。"},
{id:"assess",cn:"黄鬼王",sci:"Assessor flavissimus",len:7,cm:"6–7",zone:"洞穴",col:"全身亮黄",tem:"温和",coral:"安全",shrimp:"安全",v:"ok",terr:0,ord:24,grp:"assessor",liked:1,note:"喜欢在岩棚下倒着游，偏躲。"},
{id:"pink",cn:"粉红条纹龙",sci:"Pseudocheilinops ataenia",len:6.5,cm:"约6.5",zone:"洞穴",col:"粉橙配黄条",tem:"温和，初入躲",coral:"安全",shrimp:"安全",v:"ok",terr:0,ord:26,grp:"pink",liked:1,note:"小型隆头鱼，在石缝间穿梭。国内现货不多。"},
{id:"flash",cn:"闪光隆头",sci:"Paracheilinus spp.",len:8,cm:"7–8",zone:"中层",col:"红/紫，公鱼会炫背鳍",tem:"温和",coral:"安全",shrimp:"安全",v:"ok",terr:0,ord:28,grp:"flasher",note:"60缸里最好的中层“动起来”的鱼之一。只养1条公鱼。很会跳，必须盖网。"},
{id:"fairy",cn:"小型仙女隆头",sci:"Cirrhilabrus spp.（如 C. lubbocki）",len:10,cm:"8–10",zone:"中层",col:"多彩，种类很多",tem:"温和",coral:"安全",shrimp:"安全",v:"opt",terr:0,ord:30,grp:"flasher",note:"比闪光隆头更爱满缸游，60缸偏紧但可以。只挑小型种1条。很会跳。"},
{id:"stig",cn:"尾斑鳚",sci:"Ecsenius stigmatura",len:6,cm:"约6",zone:"停栖",col:"橙黄身，蓝灰头，尾柄一个黑点",tem:"温和",coral:"安全",shrimp:"安全",v:"ok",terr:0,ord:14,grp:"blenny",note:"趴在石头上东张西望，啄藻膜。"},
{id:"bicol",cn:"双色鳚",sci:"Ecsenius bicolor",len:10,cm:"约10",zone:"停栖",col:"前半蓝黑，后半橙",tem:"温和偏守洞",coral:"安全",shrimp:"安全",v:"ok",terr:1,ord:16,grp:"blenny",note:"住石洞、探头看人，表情丰富。鳚类二选一。"},
{id:"midas",cn:"金鳚",sci:"Ecsenius midas",len:13,cm:"约13",zone:"中层",col:"全身金黄",tem:"温和",coral:"安全",shrimp:"安全",v:"opt",terr:1,ord:18,grp:"blenny",note:"会离开石头在中层游，好看，但在鳚里偏大。"},
{id:"gramma",cn:"皇家草莓",sci:"Gramma loreto",len:8,cm:"约8",zone:"洞穴",col:"前紫后黄",tem:"守自己洞穴",coral:"安全",shrimp:"一般安全",v:"ok",terr:1,ord:55,grp:"cave",liked:1,note:"“草莓”里最推荐的一种，比真草莓（Pseudochromis）温和。"},
{id:"frid",cn:"兰花草莓",sci:"Pseudochromis fridmani",len:7,cm:"约7",zone:"洞穴",col:"全身深紫",tem:"守域较强",coral:"安全",shrimp:"可能吃很小的虾",v:"opt",terr:2,ord:60,grp:"cave",liked:1,note:"颜色极正，但会欺负雷达这类胆小鱼。草莓类只选1条。"},
{id:"pacc",cn:"双色草莓",sci:"Pictichromis paccagnellae",len:7,cm:"6–7",zone:"洞穴",col:"前紫后黄（像皇家草莓）",tem:"守域强",coral:"安全",shrimp:"可能吃很小的虾",v:"opt",terr:2,ord:60,grp:"cave",liked:1,note:"外观和皇家草莓几乎一样，脾气更差。想要这个颜色就选皇家草莓。"},
{id:"para",cn:"黄尾蓝魔",sci:"Chrysiptera parasema",len:7,cm:"约7",zone:"中下层",col:"宝蓝身，黄尾",tem:"雀鲷里较温和",coral:"安全",shrimp:"安全",v:"ok",terr:1,ord:80,grp:"damsel",liked:1,note:"蓝色位首选，国内常见。最后入缸。"},
{id:"hemi",cn:"黄肚蓝魔",sci:"Chrysiptera hemicyanea",len:7,cm:"约7",zone:"中下层",col:"上半蓝，下半黄",tem:"守域中",coral:"安全",shrimp:"安全",v:"ok",terr:1,ord:80,grp:"damsel",note:"和黄尾蓝魔二选一。"},
{id:"spring",cn:"蓝宝石魔",sci:"Chrysiptera springeri",len:5.5,cm:"约5.5",zone:"中下层",col:"全身电光蓝",tem:"守域中",coral:"安全",shrimp:"安全",v:"ok",terr:1,ord:80,grp:"damsel",note:"最小最蓝的雀鲷，国内货源少。雀鲷只选1条。"},
{id:"mand",cn:"青蛙（花斑连鳍䲗）",sci:"Synchiropus splendidus",len:7,cm:"约7",zone:"底层",col:"蓝绿橙迷彩，极艳",tem:"很温和",coral:"安全",shrimp:"安全",v:"opt",terr:0,ord:40,grp:"mand",note:"吃石头上的桡足类，新缸会饿死。开缸一年后、且只买已吃冻饵的个体再考虑。"},
{id:"sixl",cn:"六线龙",sci:"Pseudocheilinus hexataenia",len:7,cm:"约7",zone:"洞穴",col:"紫底细橙线",tem:"对温和小鱼凶",coral:"安全",shrimp:"可能挑小虾",v:"opt",terr:2,ord:85,grp:"sixline",note:"体型小但脾气大，会欺负雷达、粉红条纹龙、闪光隆头。"},
{id:"possum",cn:"金带箭龙",sci:"Wetmorella nigropinnata",len:8,cm:"7.5–8",zone:"洞穴",col:"锈红带黄环",tem:"温和，很躲",coral:"基本安全",shrimp:"会吃微小甲壳",v:"opt",terr:0,ord:26,grp:"possum",liked:1,note:"大部分时间在石缝里，看到它要靠运气。"},
{id:"flame",cn:"火焰仙",sci:"Centropyge loricula",len:10,cm:"约10",zone:"巡游",col:"红橙底，黑竖纹，蓝紫鳍边",tem:"守域中",coral:"谨慎：纽扣常被啃，可能骚扰海葵",shrimp:"安全",v:"opt",terr:1,ord:45,grp:"angel",liked:1,note:"颜值和存在感都高，本缸小型仙候选，和蓝闪电、黄新娘、渔夫仙互为备选，全缸只放1条。可能啄珊瑚，先把纽扣放可取出的底座上，持续啄食时可移走珊瑚或鱼；整组造景要预先考虑取鱼路径。"},
{id:"bisp",cn:"珊瑚美人（蓝闪电）",sci:"Centropyge bispinosa",len:10,cm:"约10",zone:"巡游",col:"蓝紫底，橙红细纹",tem:"守域中",coral:"谨慎：同火焰仙",shrimp:"安全",v:"opt",terr:1,ord:45,grp:"angel",liked:1,note:"店里叫“蓝闪电”；店里说的“石美人”其实是双色仙。本缸小型仙候选，和黄新娘、火焰仙、渔夫仙互为备选，全缸只放1条。可能啃纽扣。"},
{id:"argi",cn:"加勒比侏儒仙",sci:"Centropyge argi",len:8,cm:"约8",zone:"巡游",col:"深蓝身，橙黄脸",tem:"守域中偏强",coral:"谨慎",shrimp:"安全",v:"opt",terr:2,ord:45,grp:"angel",note:"最小的仙之一，但脾气不小。小型仙只能1条。"},
{id:"tomi",cn:"托米尼吊",sci:"Ctenochaetus tominiensis",len:16,cm:"最大16（标准体长，不含尾鳍）",zone:"巡游",col:"灰褐，黄白鳍边，脸部蓝点",tem:"温和",coral:"安全",shrimp:"安全",v:"temp",terr:1,ord:42,grp:"tang",note:"本缸主角位（2026-11-04）。体型较小的吊类之一，通常对非吊类较温和，主要刮石面和玻璃藻膜，每周至少3次补海苔。LiveAquaria建议70加仑以上，本缸过渡养，长到约10cm转给更大的缸。店里叫“火箭吊”；“三角吊”是咖啡吊，不是它。"},
{id:"kole",cn:"黄眼吊",sci:"Ctenochaetus strigosus",len:18,cm:"约18",zone:"巡游",col:"褐色细纹，金色眼圈",tem:"温和",coral:"安全",shrimp:"安全",v:"temp",terr:1,ord:42,grp:"tang",note:"成年空间比托米尼更紧张，本缸保留为过渡候选。按现有组合只考虑一只吊，购前落实后续空间。"},
{id:"ytang",cn:"黄金吊（黄三角）",sci:"Zebrasoma flavescens",len:20,cm:"约20",zone:"巡游",col:"全身亮黄",tem:"成体后守域",coral:"安全",shrimp:"安全",v:"temp",terr:2,ord:42,grp:"tang",liked:1,note:"圆身、三角轮廓、全黄，是保留的外观候选。本缸按幼鱼过渡评估，购前落实更大主缸或接手去处；不承诺固定可养年限。"},
{id:"btang",cn:"蓝吊",sci:"Paracanthurus hepatus",len:30,cm:"20–30",zone:"巡游",col:"宝蓝身，黑色调色板纹，黄尾",tem:"胆小易惊",coral:"安全",shrimp:"安全",v:"temp",terr:1,ord:42,grp:"tang",liked:1,note:"本缸第二条吊（暂定，2026-11-04）。60缸里养得最多的吊，论坛上不少养了1–2年以上；也有长到约17cm送鱼场、咬珊瑚被送走的。长得比火箭吊快、容易白点，检疫看满30天；买5–7cm，和火箭吊一样大或略大，长大或追打时转出。野外主要吃浮游小动物，冻糠虾、颗粒容易接受，另补海苔。"},
{id:"sail",cn:"大帆吊",sci:"Zebrasoma velifer / desjardinii",len:40,cm:"约40",zone:"巡游",col:"竖纹，背鳍臀鳍可大展",tem:"成体守域",coral:"安全",shrimp:"安全",v:"no",terr:2,ord:42,grp:"tang",liked:1,note:"成体比蓝吊还大，需要2米级大缸。"},
{id:"fox",cn:"狐狸 / 黄狐狸",sci:"Siganus vulpinus / unimaculatus",len:23,cm:"20–25",zone:"巡游",col:"亮黄身，黑白狐狸脸",tem:"温和",coral:"谨慎：可能啃软体",shrimp:"安全",v:"no",terr:1,ord:42,grp:"fox",liked:1,note:"体型大、吃得多，鳍棘有毒。网友推荐多是小苗阶段。"},
{id:"french",cn:"巴黎天使（法国神仙）",sci:"Pomacanthus paru",len:40,cm:"35–40",zone:"巡游",col:"幼鱼黑底黄环，成体黑灰带金边",tem:"成体守域",coral:"会啃珊瑚",shrimp:"安全",v:"no",terr:2,ord:42,grp:"bigangel",liked:1,note:"大型神仙，幼鱼好看但长得很大。"},
{id:"auriga",cn:"人字蝶",sci:"Chaetodon auriga",len:23,cm:"约23",zone:"巡游",col:"白底人字斜纹，黄尾，假眼斑",tem:"温和",coral:"会吃珊瑚和海葵",shrimp:"安全",v:"no",terr:0,ord:42,grp:"butterfly",liked:1,note:"体型和食性都不适合珊瑚缸。"},
{id:"copper",cn:"三间火箭",sci:"Chelmon rostratus",len:20,cm:"约20",zone:"巡游",col:"白底橙竖纹，长嘴",tem:"温和",coral:"谨慎",shrimp:"可能吃小虾",v:"no",terr:0,ord:42,grp:"butterfly",note:"难开口，需要大缸和成熟活石。"},
{id:"lion",cn:"双须短鳍狮",sci:"Dendrochirus biocellatus",len:13,cm:"约13",zone:"洞穴",col:"红褐斑纹，背鳍假眼",tem:"捕食者",coral:"安全",shrimp:"会吃虾和小鱼",v:"no",terr:0,ord:90,grp:"lion",liked:1,note:"体型不大，但会吃掉清洁虾、小虾虎、雷达。适合单独做主角缸。"},
{id:"chrom",cn:"青魔",sci:"Chromis viridis",len:8,cm:"约8",zone:"中层",col:"荧光蓝绿",tem:"群内互斗",coral:"安全",shrimp:"安全",v:"no",terr:1,ord:70,grp:"chromis",liked:1,note:"要5条以上群养才好看，60缸里会互斗到只剩1–2条。"},
{id:"humbug",cn:"四间雀",sci:"Dascyllus aruanus",len:8,cm:"约8",zone:"中下层",col:"白底黑粗竖纹",tem:"很凶",coral:"安全",shrimp:"安全",v:"no",terr:2,ord:80,grp:"damsel",liked:1,note:"雀鲷里最凶的一类，会追咬全缸。"},
{id:"domino",cn:"三点白",sci:"Dascyllus trimaculatus",len:14,cm:"约14",zone:"中下层",col:"黑身三白点",tem:"很凶",coral:"安全",shrimp:"安全",v:"no",terr:2,ord:80,grp:"damsel",note:"长大后又大又凶。"},
{id:"maroon",cn:"透红小丑",sci:"Premnas biaculeatus",len:15,cm:"雌约15",zone:"中下层",col:"深酒红，白/金环",tem:"雌鱼很凶",coral:"安全",shrimp:"安全",v:"no",terr:2,ord:50,grp:"clown",note:"和公子小丑不能同缸，单独养也偏凶。"},
{id:"anth",cn:"金花（金拟花鮨）",sci:"Pseudanthias squamipinnis",len:15,cm:"约15",zone:"中层",col:"橙金，公鱼粉紫",tem:"群居",coral:"安全",shrimp:"安全",v:"no",terr:1,ord:70,grp:"anthias",note:"需要群养、一天多次喂，60缸负荷太大。"},
{id:"sleep",cn:"黄头虾虎（翻砂虾虎）",sci:"Valenciennea strigata",len:18,cm:"约18",zone:"底层",col:"白身黄头蓝纹",tem:"温和",coral:"翻砂盖住低处珊瑚",shrimp:"安全",v:"no",terr:0,ord:10,grp:"sandgoby",note:"靠翻砂找食，砂床小的缸常饿瘦。想要虾虎选黄守望。"},
{id:"perc",cn:"真公子小丑",sci:"Amphiprion percula",len:11,cm:"8–11",zone:"中下层",col:"橙色更艳，黑边更粗",tem:"成对后守地盘",coral:"安全",shrimp:"安全",v:"ok",terr:1,ord:50,grp:"clown",unit:2,note:"和公子小丑几乎一样，黑边更明显。两种小丑二选一，只养一对。"},
{id:"frena",cn:"番茄小丑",sci:"Amphiprion frenatus",len:14,cm:"雌约14",zone:"中下层",col:"番茄红，头后一道白环",tem:"雌鱼凶",coral:"安全",shrimp:"安全",v:"no",terr:2,ord:50,grp:"clown",note:"长大后体型大、脾气凶，会压制其他鱼。"},
{id:"allen",cn:"艾伦雀鲷",sci:"Pomacentrus alleni",len:6,cm:"约6",zone:"中下层",col:"亮蓝，尾鳍下缘橙黄",tem:"雀鲷里较温和",coral:"安全",shrimp:"安全",v:"ok",terr:1,ord:80,grp:"damsel",note:"体型小、颜色接近蓝宝石魔。国内商品名不统一，按学名核对。雀鲷只选1条。"},
{id:"cyan",cn:"蓝魔鬼",sci:"Chrysiptera cyanea",len:8.5,cm:"约8.5",zone:"中下层",col:"全身宝蓝，公鱼尾鳍橙",tem:"凶，越大越凶",coral:"安全",shrimp:"安全",v:"no",terr:2,ord:80,grp:"damsel",note:"便宜常见，但会追咬后进的鱼。蓝色位选黄尾蓝魔。"},
{id:"neon",cn:"霓虹虾虎",sci:"Elacatinus oceanops",len:5,cm:"约5",zone:"停栖",col:"黑身，一条电光蓝纵线",tem:"温和",coral:"安全",shrimp:"安全",v:"ok",terr:0,ord:13,grp:"neon",note:"会给其他鱼做清洁，人工繁殖个体好养。可养1条或一对。"},
{id:"wheel",cn:"粉红守望",sci:"Amblyeleotris wheeleri",len:8,cm:"约8",zone:"底层",col:"白底粉红宽竖带，蓝点",tem:"温和",coral:"安全",shrimp:"安全",v:"ok",terr:1,ord:10,grp:"sandgoby",note:"和黄守望同类，可配枪虾共生。砂洞守望虾虎二选一。"},
{id:"hifin",cn:"高鳍虾虎",sci:"Stonogobiops nematodes",len:5,cm:"约5",zone:"底层",col:"白身黑斜带，黄头，丝状高背鳍",tem:"温和",coral:"安全",shrimp:"安全",v:"ok",terr:0,ord:11,grp:"hifin",note:"小巧，悬停在洞口上方，可配枪虾。很会跳。"},
{id:"lawn",cn:"胡子鳚（除藻鳚）",sci:"Salarias fasciatus",len:13,cm:"约13",zone:"停栖",col:"斑驳褐绿，头顶触须",tem:"对同类凶",coral:"安全",shrimp:"安全",v:"opt",terr:1,ord:16,grp:"blenny",note:"表情憨，靠啃藻生活。新缸藻不够容易饿瘦，要买能吃人工藻片的个体。"},
{id:"mela",cn:"黑顶丝鲈",sci:"Gramma melacara",len:10,cm:"约10",zone:"洞穴",col:"深紫身，背鳍黑边",tem:"守洞穴",coral:"安全",shrimp:"一般安全",v:"opt",terr:1,ord:55,grp:"cave",note:"皇家草莓的近亲，全身深紫，略大略贵。草莓类只选1条。"},
{id:"ywr",cn:"黄龙（金黄海猪鱼）",sci:"Halichoeres chrysus",len:12,cm:"约12",zone:"中层",col:"全身金黄，背鳍黑点",tem:"温和",coral:"安全",shrimp:"可能挑很小的甲壳",v:"opt",terr:0,ord:32,grp:"ywrasse",note:"满缸游，晚上钻砂睡，需要局部5cm以上细砂（你的砂约3cm）。会吃扁虫等害虫。"},
{id:"herald",cn:"黄新娘",sci:"Centropyge heraldi",len:12,cm:"最大12（全长）",zone:"巡游",col:"全身亮黄",tem:"守域中",coral:"谨慎：可能啃纽扣",shrimp:"安全",v:"opt",terr:1,ord:45,grp:"angel",note:"全黄、高身形，本缸小型仙候选，和蓝闪电、火焰仙、渔夫仙互为备选，全缸只放1条。成年空间与啄珊瑚风险分别评估；本方案只选一只小型仙，纽扣用可移出的底座。"},
{id:"aura",cn:"火背仙",sci:"Centropyge aurantonotus",len:7.5,cm:"最大7.5（全长）",zone:"巡游",col:"深蓝身，橙色背",tem:"守域中",coral:"谨慎",shrimp:"安全",v:"opt",terr:1,ord:45,grp:"angel",note:"用户2026-11-04明确不喜欢外观，已从本缸首选和备选撤出；资料库保留物种资料。"},
{id:"bicang",cn:"双色仙（店里叫石美人）",sci:"Centropyge bicolor",len:15,cm:"约15",zone:"巡游",col:"前黄后深蓝",tem:"守域强",coral:"谨慎",shrimp:"安全",v:"no",terr:2,ord:45,grp:"angel",note:"小型仙里偏大偏凶。"},
{id:"helf",cn:"海氏雷达",sci:"Nemateleotris helfrichi",len:6,cm:"约6",zone:"中层",col:"黄头，渐变淡紫身",tem:"很温和",coral:"安全",shrimp:"安全",v:"opt",terr:0,ord:20,grp:"firefish",note:"最漂亮也最贵的雷达，深水种，较难养。雷达类只养1条。"},
{id:"spotm",cn:"花斑青蛙",sci:"Synchiropus picturatus",len:7,cm:"约7",zone:"底层",col:"绿底，黑环包橙圈的斑点",tem:"很温和",coral:"安全",shrimp:"安全",v:"opt",terr:0,ord:40,grp:"mand",note:"和青蛙同类、要求一样，二选一。"},
{id:"powder",cn:"粉蓝吊",sci:"Acanthurus leucosternon",len:23,cm:"约23",zone:"巡游",col:"粉蓝身，黑脸白下巴，黄背鳍",tem:"守域强",coral:"安全",shrimp:"安全",v:"no",terr:2,ord:42,grp:"tang",note:"需要大缸，极易爆白点。"},
{id:"purple",cn:"紫吊",sci:"Zebrasoma xanthurum",len:25,cm:"约25",zone:"巡游",col:"全身紫，黄尾",tem:"守域强",coral:"安全",shrimp:"安全",v:"no",terr:2,ord:42,grp:"tang",note:"颜色漂亮，但成体大、脾气大。"},
{id:"naso",cn:"天狗吊",sci:"Naso lituratus",len:45,cm:"约45",zone:"巡游",col:"灰身，橙唇黄额",tem:"温和",coral:"安全",shrimp:"安全",v:"no",terr:1,ord:42,grp:"tang",note:"游得快、长得很大，需要2米以上大缸。"},
{id:"forci",cn:"黄长嘴",sci:"Forcipiger flavissimus",len:22,cm:"约22",zone:"巡游",col:"亮黄身，黑白头，长嘴",tem:"温和",coral:"谨慎",shrimp:"会吃小虾",v:"no",terr:0,ord:42,grp:"butterfly",note:"体型太大，会啄虾和管虫。"},
{id:"henio",cn:"黑白关刀",sci:"Heniochus diphreutes",len:20,cm:"约20",zone:"巡游",col:"白身黑宽带，长丝背鳍",tem:"温和，喜群游",coral:"谨慎",shrimp:"安全",v:"no",terr:0,ord:42,grp:"butterfly",note:"体高很高，需要大缸群养。"},
{id:"toby",cn:"尖嘴河豚",sci:"Canthigaster valentini",len:10,cm:"约10",zone:"巡游",col:"白底黑鞍斑，橙点",tem:"温和",coral:"会啃软体、纽扣",shrimp:"会吃虾",v:"no",terr:0,ord:42,grp:"toby",note:"很可爱，但会啃珊瑚和清洁虾。"},
{id:"boxf",cn:"黄金木瓜",sci:"Ostracion cubicus",len:45,cm:"约45",zone:"巡游",col:"幼鱼明黄带黑点，方盒子身形",tem:"温和",coral:"谨慎",shrimp:"会吃虾",v:"no",terr:0,ord:42,grp:"boxfish",note:"幼鱼像个小骰子，但能长得很大，受惊放毒可能毒死全缸。"},
{id:"leaf",cn:"枯叶鱼",sci:"Taenianotus triacanthus",len:10,cm:"约10",zone:"停栖",col:"像一片叶子，有白黄红黑多色",tem:"伏击捕食",coral:"安全",shrimp:"会吃虾",v:"no",terr:0,ord:90,grp:"lion",note:"会随水流左右摇晃，非常特别；但会吞掉虾和小鱼，适合单独养。"},
{id:"perid",cn:"粉红小丑",sci:"Amphiprion perideraion",len:10,cm:"约10",zone:"中下层",col:"粉橙身，背上一道白线，头后细白环",tem:"较胆小",coral:"安全",shrimp:"安全",v:"opt",terr:1,ord:50,grp:"clown",unit:2,note:"颜色很柔，比公子小丑胆小，没有海葵时更紧张。小丑只养一对。"},
{id:"clarkii",cn:"克氏小丑",sci:"Amphiprion clarkii",len:15,cm:"约15",zone:"中下层",col:"黑橙身，三道白环，黄尾",tem:"凶",coral:"安全",shrimp:"安全",v:"no",terr:2,ord:50,grp:"clown",note:"体型大、脾气凶，60缸会压制其他鱼。"},
{id:"histrio",cn:"绿蟋蟀",sci:"Gobiodon histrio",len:3.5,cm:"约3.5",zone:"停栖",col:"绿身，红色细纹和斑点",tem:"温和",coral:"基本安全",shrimp:"安全",v:"ok",terr:0,ord:12,grp:"gobiodon",note:"和黄小丑虾虎同类，颜色更特别。蟋蟀类只选1条。"},
{id:"macn",cn:"蓝鬼王",sci:"Assessor macneilli",len:6,cm:"约6",zone:"洞穴",col:"全身深蓝",tem:"温和",coral:"安全",shrimp:"安全",v:"ok",terr:0,ord:24,grp:"assessor",note:"黄鬼王的蓝色版，温和，适合喜欢蓝色又不想要雀鲷脾气的你。和黄鬼王二选一。"},
{id:"oual",cn:"黄金獠牙鳚",sci:"Meiacanthus oualanensis",len:10,cm:"约10",zone:"中层",col:"全身柠檬黄",tem:"温和",coral:"安全",shrimp:"安全",v:"ok",terr:0,ord:18,grp:"fang",note:"在中层游动，不像普通鳚趴着。牙有毒但只用于自卫，其他鱼不敢吃它。国内商品名不统一，按学名核对。"},
{id:"gram",cn:"条纹獠牙鳚",sci:"Meiacanthus grammistes",len:11,cm:"约11",zone:"中层",col:"黄白身，黑色纵纹",tem:"温和",coral:"安全",shrimp:"安全",v:"ok",terr:0,ord:18,grp:"fang",note:"和黄金獠牙鳚同类，二选一。"},
{id:"cyano",cn:"金线天竺鲷",sci:"Ostorhinchus cyanosoma",len:8,cm:"约8",zone:"中层",col:"银身，几道金橙色纵线",tem:"很温和",coral:"安全",shrimp:"安全",v:"ok",terr:0,ord:22,grp:"apogon",note:"可养2–3条小群，安静悬停。白天偏躲，喂食时最活跃。"},
{id:"spring2",cn:"斯氏草莓",sci:"Pseudochromis springeri",len:6,cm:"约6",zone:"洞穴",col:"黑身，头部细蓝线",tem:"守域较强",coral:"安全",shrimp:"可能吃很小的虾",v:"opt",terr:2,ord:60,grp:"cave",note:"小而精致，但脾气比皇家草莓差。草莓类只选1条。"},
{id:"comet",cn:"珍珠鬼王（海水斗鱼）",sci:"Calloplesiops altivelis",len:16,cm:"约16",zone:"洞穴",col:"深褐满身白点，尾部假眼斑",tem:"温和，很躲",coral:"安全",shrimp:"可能吃小虾",v:"opt",terr:0,ord:35,grp:"comet",note:"长相很特别。淘宝上叫“珍珠鬼王”；淘宝的“珍珠龙”多半是另一种隆头鱼，别搞混。但成体偏大，白天多躲在岩洞里。"},
{id:"armat",cn:"火焰格",sci:"Neocirrhites armatus",len:9,cm:"约9",zone:"停栖",col:"全身艳红，眼周黑圈",tem:"守域中",coral:"安全",shrimp:"可能吃小虾",v:"opt",terr:1,ord:70,grp:"hawk",note:"喜欢停在珊瑚和石头顶上东张西望，极红。会吃小型虾，清洁虾一般较安全，但不能保证。"},
{id:"typus",cn:"尖嘴格",sci:"Oxycirrhites typus",len:13,cm:"约13",zone:"停栖",col:"白底红格纹，长嘴",tem:"捕食小虾",coral:"安全",shrimp:"会吃虾",v:"no",terr:1,ord:70,grp:"hawk",note:"会吃清洁虾等小虾，和你的虾计划冲突。"},
{id:"emper",cn:"皇帝神仙",sci:"Pomacanthus imperator",len:40,cm:"约40",zone:"巡游",col:"幼鱼蓝底白圈，成体蓝黄横纹",tem:"成体守域",coral:"会啃珊瑚",shrimp:"安全",v:"no",terr:2,ord:42,grp:"bigangel",note:"国内很常见的大型神仙，幼鱼便宜好看，但会长到40cm。"},
{id:"volit",cn:"魔鬼蓑鲉（狮子鱼）",sci:"Pterois volitans",len:38,cm:"约38",zone:"巡游",col:"红白相间竖纹，大扇形胸鳍",tem:"捕食者",coral:"安全",shrimp:"会吃虾和小鱼",v:"no",terr:0,ord:90,grp:"lion",note:"最常见的狮子鱼，体型大、会吞小鱼，鳍棘有毒。"},
{id:"clownt",cn:"小丑炮弹",sci:"Balistoides conspicillum",len:50,cm:"约50",zone:"巡游",col:"黑身下腹大白点，黄色网纹",tem:"很凶",coral:"会咬无脊椎",shrimp:"会吃虾",v:"no",terr:2,ord:42,grp:"trigger",note:"花色极抢眼，但又大又凶，只适合大型纯鱼缸。"},
{id:"garden",cn:"花园鳗（斑点花园鳗）",sci:"Heteroconger hassi",len:40,cm:"35–40（大半身埋在砂里）",zone:"底层",col:"白底黑斑，竖在砂里摇摆",tem:"很温和，极胆小",coral:"安全",shrimp:"安全",v:"no",terr:0,ord:9,grp:"garden",note:"需要至少15cm、最好20cm以上的细砂，要3条以上成群养，一天喂几次细小饵。你的砂约3cm，现有造景下放不下。只有另做深砂专区才有机会。"},
{id:"dart",cn:"喷射机（鳍塘鳢）",sci:"Ptereleotris spp.（如 P. zebra、P. evides）",len:11,cm:"10–12",zone:"中层",col:"淡蓝或淡紫，细长，种类不同有斑马纹或黑尾",tem:"很温和，胆小",coral:"安全",shrimp:"安全",v:"ok",terr:0,ord:21,grp:"dart",note:"雷达的近亲，会在中层成片悬停游动，能补“缺一条游动的鱼”。店里多叫“喷射机”。“鸳鸯”不是它：画眉鸳鸯是双色獠牙鳚，美国大帆鸳鸯是黄头后颌鱼。可养1条或已配好的一对。极会跳，必须盖网。"},
{id:"yasha",cn:"红线天线虾虎",sci:"Stonogobiops yasha",len:5,cm:"约5",zone:"底层",col:"白身橙红斜线，黑色长背鳍",tem:"温和",coral:"安全",shrimp:"安全",v:"ok",terr:0,ord:11,grp:"hifin",note:"小、颜色干净，在洞口上方悬停，常和枪虾共生。商品名对应关系到店确认。和高鳍虾虎同类二选一，会跳。"},
{id:"jaw",cn:"黄头后颌鱼（吐沙鱼）",sci:"Opistognathus aurifrons",len:10,cm:"约10",zone:"底层",col:"淡蓝身，亮黄头",tem:"温和",coral:"安全",shrimp:"安全",v:"opt",terr:1,ord:10,grp:"jaw",note:"自己用碎石砂挖竖洞，常探出半身看人，感觉接近花园鳗但养得起。需要一块深约10cm、混碎珊瑚的砂区（你的砂约3cm），和黄守望抢砂面，二者择一更稳。极会跳，必须盖网。"},
{id:"signal",cn:"四驱车虾虎",sci:"Signigobius biocellatus",len:6.5,cm:"约6.5",zone:"底层",col:"灰褐，背鳍两个大眼斑",tem:"温和",coral:"安全",shrimp:"安全",v:"no",terr:0,ord:10,grp:"sandgoby",note:"靠吞砂筛食底栖小生物，新缸几乎都会饿瘦，需成熟大砂床。"},
{id:"puell",cn:"钻石哨兵",sci:"Valenciennea puellaris",len:15,cm:"约15",zone:"底层",col:"白身橙色斑点",tem:"温和",coral:"翻砂盖住低处珊瑚",shrimp:"安全",v:"no",terr:0,ord:10,grp:"sandgoby",note:"翻砂虾虎，体型偏大，砂床小的缸常饿瘦。"},
{id:"leopard",cn:"豹纹龙 / 花豹龙",sci:"Macropharyngodon meleagris",len:15,cm:"约15",zone:"中层",col:"雌鱼白底密布黑斑，雄鱼绿底橙纹",tem:"温和",coral:"安全",shrimp:"可能挑小甲壳",v:"no",terr:0,ord:32,grp:"leopard",note:"很难开口，需要成熟活石和厚砂睡觉，新缸不建议。"},
{id:"labro",cn:"飘飘 / 医生鱼",sci:"Labroides dimidiatus",len:11,cm:"约11",zone:"中层",col:"蓝白身，一条黑纵带",tem:"温和",coral:"安全",shrimp:"安全",v:"no",terr:0,ord:30,grp:"labro",note:"野外专吃别的鱼身上的寄生虫，鱼缸里多数会慢慢饿死。清洁工作交给医生虾。"},
{id:"seahorse",cn:"海马（人工繁殖）",sci:"Hippocampus kuda 等",len:15,cm:"12–17",zone:"停栖",col:"黄、黑、橙多色",tem:"很温和，游得慢",coral:"会被刺胞珊瑚和海葵蜇",shrimp:"安全",v:"no",terr:0,ord:90,grp:"seahorse",note:"抢不过小丑、雀鲷，也怕奶嘴海葵，只适合做单独的海马缸。"},
{id:"kath",cn:"凯瑟琳仙女龙",sci:"Cirrhilabrus katherinae",len:9,cm:"约9",zone:"中层",col:"公鱼粉红身，背部紫红，鳍缘带蓝",tem:"温和",coral:"安全",shrimp:"安全",v:"ok",terr:0,ord:30,grp:"flasher",note:"小型仙女隆头，满缸游、公鱼炫鳍很好看。水族名录确认“凯瑟琳雀”就是它。闪光/仙女隆头只养1条公鱼，很会跳。"},
{id:"atrod",cn:"双色獠牙鳚",sci:"Meiacanthus atrodorsalis",len:11,cm:"约11",zone:"中层",col:"前半淡蓝灰，后半亮黄，眼后一道黑线",tem:"温和",coral:"安全",shrimp:"安全",v:"ok",terr:0,ord:18,grp:"fang",note:"在中层游的鳚，蓝黄配色接近你喜欢的蓝色鱼但不守域。獠牙鳚类只选1条。"},
{id:"swiss",cn:"红纹鲈（瑞士卫兵）",sci:"Liopropoma rubre",len:8,cm:"约8",zone:"洞穴",col:"红黄相间纵纹，尾鳍两个黑斑",tem:"温和，很躲",coral:"安全",shrimp:"可能吃很小的虾",v:"opt",terr:0,ord:34,grp:"swiss",note:"颜色很精致，但白天多在石缝里，偏贵、国内货少。商品名不统一，按学名问。"},
{id:"rolland",cn:"罗氏雀鲷",sci:"Chrysiptera rollandi",len:7.5,cm:"约7.5",zone:"中下层",col:"蓝灰到深色身，腹尾偏白或淡黄，地区色差大",tem:"雀鲷里很温和",coral:"安全",shrimp:"安全",v:"ok",terr:1,ord:80,grp:"damsel",note:"最温和的雀鲷之一。颜色比黄尾蓝魔素，到店看实物。雀鲷只选1条。"},
{id:"taupou",cn:"斐济魔",sci:"Chrysiptera taupou",len:8,cm:"约8",zone:"中下层",col:"亮蓝身，黄腹黄尾",tem:"凶",coral:"安全",shrimp:"安全",v:"no",terr:2,ord:80,grp:"damsel",note:"淘宝很常见，长得像黄肚蓝魔，但脾气凶得多。"},
{id:"randal",cn:"兰道守望",sci:"Amblyeleotris randalli",len:12,cm:"约12",zone:"底层",col:"白底橙色竖带，背鳍大黑眼斑",tem:"温和",coral:"安全",shrimp:"安全",v:"opt",terr:1,ord:10,grp:"sandgoby",note:"可配枪虾，背鳍展开很好看，比黄守望略大。砂洞守望虾虎只放1条。"},
{id:"falco",cn:"尖头格（斑点鹰）",sci:"Cirrhitichthys falco",len:7,cm:"约7",zone:"停栖",col:"白底红褐斑块，背鳍尖端有须",tem:"守域中",coral:"安全",shrimp:"会吃小虾",v:"opt",terr:1,ord:70,grp:"hawk",note:"最小的格类，停在石顶看人。和清洁虾混养有风险，体型大的清洁虾较安全但不保证。格类只选1条。"},
{id:"acanth",cn:"非洲侏儒仙",sci:"Centropyge acanthops",len:8,cm:"约8",zone:"巡游",col:"深蓝身，橙黄背和头，尾鳍透明",tem:"守域中",coral:"谨慎：可能啃纽扣",shrimp:"安全",v:"opt",terr:1,ord:45,grp:"angel",note:"小型仙候选，蓝身橙背；成年空间、领地和啄珊瑚风险需一起评估。本方案只考虑一只小型仙，不能只按体长决定适配。"},
{id:"filef",cn:"除海葵马面（伪装鲀）",sci:"Acreichthys tomentosus",len:10,cm:"约10",zone:"停栖",col:"灰褐绿斑驳，会变色伪装",tem:"温和",coral:"谨慎：可能啄纽扣",shrimp:"安全",v:"opt",terr:0,ord:40,grp:"file",note:"会吃害虫艾氏海葵（Aiptasia），长相古怪可爱。缸里没海葵害时它可能改啄纽扣，常被当成“工具鱼”临时养。"},
{id:"rainf",cn:"雷氏虾虎（彩线虾虎）",sci:"Koumansetta rainfordi",len:6.5,cm:"约6.5",zone:"停栖",col:"橙黄底，蓝紫和黑色纵线，背鳍眼斑",tem:"温和",coral:"安全",shrimp:"安全",v:"opt",terr:0,ord:14,grp:"rainf",note:"很好看，但主要啄石头上的藻和微生物，新缸容易饿瘦。等开缸半年后、买已吃冻饵的个体。"},
{id:"melan",cn:"彩虹龙（尾斑海猪鱼）",sci:"Halichoeres melanurus",len:12,cm:"约12",zone:"中层",col:"橙蓝相间纵纹，尾部黑斑",tem:"温和",coral:"安全",shrimp:"可能挑很小的甲壳",v:"opt",terr:0,ord:32,grp:"ywrasse",note:"满缸游、会吃扁虫。晚上钻砂睡，需要一块5cm以上细砂。“彩虹龙”这个商品名也被用在别的隆头鱼上，按学名核对。和黄龙二选一。"},
{id:"new_auranti",cn:"麒麟神仙",sci:"Centropyge aurantia","len":10.0,"cm":"最大记录10（全长）","zone":"巡游","col":"橙红身细红纹","tem":"视个体及同伴","coral":"谨慎：可能啄珊瑚","shrimp":"一般需观察","v":"opt","terr":1,"ord":45,"grp":"angel","note":"可替换小型仙位（三选一）；较躲，先确认稳定开口；可能啄纽扣，成熟缸和可拆珊瑚底座。"},
{id:"new_colini",cn:"紫背仙",sci:"Centropyge colini","len":9.0,"cm":"最大记录9（全长）","zone":"巡游","col":"亮黄身蓝紫背","tem":"视个体及同伴","coral":"谨慎：可能啄珊瑚","shrimp":"一般需观察","v":"opt","terr":1,"ord":45,"grp":"angel","note":"可替换小型仙位（三选一）；偏躲，需岩洞和已开口个体；可能啄纽扣，价格较高。"},
{id:"new_fisheri",cn:"渔夫仙",sci:"Centropyge fisheri","len":8.4,"cm":"最大记录8.4（全长）","zone":"巡游","col":"按产地两种颜色：深蓝紫身、尾巴淡黄白（照片这种，原来叫白尾仙）；夏威夷的是橙红身蓝边","tem":"视个体及同伴","coral":"谨慎：可能啄珊瑚","shrimp":"一般需观察","v":"opt","terr":1,"ord":45,"grp":"angel","note":"本缸小型仙备选（2026-11-05），和蓝闪电、黄新娘、火焰仙四选一。FishBase把白尾仙（C. flavicauda）并进了这个种，所以同叫渔夫仙，颜色按产地差很多：印度洋、西太平洋的多是深蓝紫色，夏威夷的是橙色。买前让店里拍实物照片。成体约8.4cm，小型仙里偏小；需成熟石面和多样饵料，可能啄纽扣。"},
{id:"new_flaviss",cn:"柠檬批",sci:"Centropyge flavissima","len":14.0,"cm":"最大记录14（全长）","zone":"巡游","col":"明黄身和蓝眼圈","tem":"视个体及同伴","coral":"谨慎：可能啄珊瑚","shrimp":"一般需观察","v":"opt","terr":1,"ord":45,"grp":"angel","note":"可替换小型仙位（三选一）；可能啄珊瑚及砗磲，体型较大需游泳空间；先备后续转出。"},
{id:"new_multisp",cn:"蓝翅黑仙",sci:"Centropyge multispinis","len":14.0,"cm":"最大记录14（全长）","zone":"巡游","col":"深色身和蓝色鳍缘","tem":"视个体及同伴","coral":"谨慎：可能啄珊瑚","shrimp":"一般需观察","v":"opt","terr":1,"ord":45,"grp":"angel","note":"可替换小型仙位（三选一）；成鱼较大、可能啄纽扣；先确认后续空间。"},
{id:"new_venusta",cn:"黄肚仙",sci:"Centropyge venusta","len":12.0,"cm":"最大记录12（长度口径未说明）","zone":"巡游","col":"紫蓝背金黄腹","tem":"视个体及同伴","coral":"谨慎：可能啄珊瑚","shrimp":"一般需观察","v":"opt","terr":1,"ord":45,"grp":"angel","note":"可替换小型仙位（三选一）；较躲且开口需留意，可能啄纽扣；长度口径未说明。"},
{id:"new_vrolik",cn:"黑尾新娘",sci:"Centropyge vrolikii","len":12.0,"cm":"最大记录12（全长）","zone":"巡游","col":"浅灰前身、深色尾部","tem":"视个体及同伴","coral":"谨慎：可能啄珊瑚","shrimp":"一般需观察","v":"opt","terr":1,"ord":45,"grp":"angel","note":"可替换小型仙位（三选一）；活石觅食，可能啄珊瑚；只选一条小型仙。"},
{id:"new_eibli",cn:"虎纹仙",sci:"Centropyge eibli","len":15.0,"cm":"最大记录15（全长）","zone":"巡游","col":"银白身橙色竖纹黑尾","tem":"视个体及同伴","coral":"谨慎：可能啄珊瑚","shrimp":"一般需观察","v":"opt","terr":1,"ord":45,"grp":"angel","note":"可替换小型仙位（三选一）；体型较大，可能啄珊瑚；准备后续空间。"},
{id:"new_rex",cn:"紫头魔",sci:"Chrysiptera rex","len":7.0,"cm":"最大记录7（全长）","zone":"中下层","col":"黄橙头、浅色身带蓝点","tem":"视个体及同伴","coral":"视物种与个体","shrimp":"一般需观察","v":"opt","terr":1,"ord":80,"grp":"damsel","note":"可替换黄尾蓝魔位；雀鲷有领地性，最后入缸，关注对雷达的追逐。"},
{id:"new_starki",cn:"深水蓝魔",sci:"Chrysiptera starcki","len":7,"cm":"最大记录7（标准体长，不含尾鳍）","zone":"中下层","col":"蓝身黄色背部","tem":"视个体及同伴","coral":"视物种与个体","shrimp":"一般需观察","v":"opt","terr":1,"ord":80,"grp":"damsel","note":"可替换黄尾蓝魔位；标准体长不含尾鳍；个体守域且价格较高，后入缸并观察追咬。"},
{id:"new_talboti",cn:"太阳魔",sci:"Chrysiptera talboti","len":6.0,"cm":"最大记录6（全长）","zone":"中下层","col":"黄脸粉紫身、背鳍黑斑","tem":"视个体及同伴","coral":"视物种与个体","shrimp":"一般需观察","v":"opt","terr":1,"ord":80,"grp":"damsel","note":"可替换黄尾蓝魔位；只选一条雀鲷，最后入缸，留意个体守域。"},
{id:"new_aurivent",cn:"蓝天堂",sci:"Pomacentrus auriventris","len":5.5,"cm":"最大记录5.5（标准体长，不含尾鳍）","zone":"中下层","col":"蓝身黄腹","tem":"视个体及同伴","coral":"视物种与个体","shrimp":"一般需观察","v":"opt","terr":1,"ord":80,"grp":"damsel","note":"可替换黄尾蓝魔位；标准体长不含尾鳍；仅选一条雀鲷，观察领地。"},
{id:"new_coelestis",cn:"电光魔",sci:"Pomacentrus coelestis","len":9.0,"cm":"最大记录9（全长）","zone":"中下层","col":"明亮蓝身黄色鳍边","tem":"视个体及同伴","coral":"视物种与个体","shrimp":"一般需观察","v":"opt","terr":1,"ord":80,"grp":"damsel","note":"可替换黄尾蓝魔位；只选一条雀鲷，最后入缸并观察追逐。"},
{id:"new_molucc",cn:"黄魔",sci:"Pomacentrus moluccensis","len":9.0,"cm":"最大记录9（全长）","zone":"中下层","col":"明黄色、深色眼部","tem":"视个体及同伴","coral":"视物种与个体","shrimp":"一般需观察","v":"opt","terr":1,"ord":80,"grp":"damsel","note":"可替换黄尾蓝魔位；雀鲷有领地性，最后入缸，留意与小鱼冲突。"},
{id:"new_ephipp",cn:"红苹果小丑",sci:"Amphiprion ephippium","len":14.0,"cm":"最大记录14（全长）","zone":"中下层","col":"橙红身、成年有黑斑","tem":"视个体及同伴","coral":"视物种与个体","shrimp":"一般需观察","v":"opt","terr":1,"ord":45,"grp":"clown","note":"可替换公子小丑一对；替换整对公子；成体较大且守域，幼鱼与成鱼颜色不同。"},
{id:"new_melanop",cn:"黑红小丑",sci:"Amphiprion melanopus","len":12.0,"cm":"最大记录12（全长）","zone":"中下层","col":"橙红身和黑色侧斑","tem":"视个体及同伴","coral":"视物种与个体","shrimp":"一般需观察","v":"opt","terr":1,"ord":45,"grp":"clown","note":"可替换公子小丑一对；替换整对公子；成对后可能守域。"},
{id:"new_polymn",cn:"黑豹小丑",sci:"Amphiprion polymnus","len":13.0,"cm":"最大记录13（全长）","zone":"中下层","col":"黑白鞍纹与橙色口鼻","tem":"视个体及同伴","coral":"视物种与个体","shrimp":"一般需观察","v":"opt","terr":1,"ord":45,"grp":"clown","note":"可替换公子小丑一对；替换整对公子；需配好对并留领地。"},
{id:"new_guttata",cn:"橙点虾虎",sci:"Amblyeleotris guttata","len":11.0,"cm":"最大记录11（标准体长，不含尾鳍）","zone":"底层","col":"浅色身橙色斑点","tem":"视个体及同伴","coral":"视物种与个体","shrimp":"一般需观察","v":"opt","terr":0,"ord":45,"grp":"sandgoby","note":"可替换黄守望位；标准体长不含尾鳍；提供可挖洞砂区，核枪虾配对并防跳。"},
{id:"new_yanoi",cn:"太平洋粉条虾虎",sci:"Amblyeleotris yanoi","len":13.0,"cm":"最大记录13（标准体长，不含尾鳍）","zone":"底层","col":"浅色身粉橙横带","tem":"视个体及同伴","coral":"视物种与个体","shrimp":"一般需观察","v":"opt","terr":0,"ord":45,"grp":"sandgoby","note":"可替换黄守望位；标准体长不含尾鳍；提供洞区、确认与枪虾共生并防跳。"},
{id:"new_griess",cn:"火炬虾虎",sci:"Discordipinna griessingeri","len":3.0,"cm":"最大记录3（标准体长，不含尾鳍）","zone":"底层","col":"白橙条纹和高背鳍","tem":"视个体及同伴","coral":"视物种与个体","shrimp":"一般需观察","v":"opt","terr":0,"ord":45,"grp":"other","note":"可替换黄守望位；体型极小且躲藏；细食点喂，鱼梳防吸入，慎与大鱼混养。"},
{id:"new_figaro",cn:"金灯虾虎",sci:"Elacatinus figaro","len":3.4,"cm":"最大记录3.4（标准体长，不含尾鳍）","zone":"洞穴","col":"暗身黄线","tem":"视个体及同伴","coral":"视物种与个体","shrimp":"一般需观察","v":"opt","terr":1,"ord":45,"grp":"neon","note":"可替换蓝鬼王位；标准体长不含尾鳍；体型小需细食和防吸入口，较贵。"},
{id:"new_atrang",cn:"黑蟋蟀",sci:"Gobiodon atrangulatus","len":3.5,"cm":"最大记录3.5（全长）","zone":"停栖","col":"深色小身形","tem":"视个体及同伴","coral":"视物种与个体","shrimp":"一般需观察","v":"opt","terr":0,"ord":45,"grp":"gobiodon","note":"可替换柠檬蟋蟀位；小嘴需细食点喂；野外生活于鹿角珊瑚间，纯软体缸是否易适应待核，可能啄硬珊瑚，替换蟋蟀位。"},
{id:"new_hectori",cn:"金线虾虎",sci:"Koumansetta hectori","len":8.5,"cm":"最大记录8.5（标准体长，不含尾鳍）","zone":"底层","col":"深身黄色纵线","tem":"视个体及同伴","coral":"视物种与个体","shrimp":"一般需观察","v":"opt","terr":0,"ord":45,"grp":"rainf","note":"可替换黄守望位；需成熟石面和已开口个体；标准体长不含尾鳍。"},
{id:"new_exiguus",cn:"短身裸叶虾虎",sci:"Lubricogobius exiguus","len":4.0,"cm":"最大记录4（标准体长，不含尾鳍）","zone":"停栖","col":"明黄小鱼","tem":"视个体及同伴","coral":"视物种与个体","shrimp":"一般需观察","v":"opt","terr":0,"ord":45,"grp":"gobiodon","note":"可替换柠檬蟋蟀位；个体细小需细食、遮蔽和防吸入；标准体长不含尾鳍。"},
{id:"new_bella",cn:"贝拉虾虎",sci:"Valenciennea bella","len":6.9,"cm":"最大记录6.9（标准体长，不含尾鳍）","zone":"底层","col":"浅身细条与橙色标记","tem":"视个体及同伴","coral":"视物种与个体","shrimp":"一般需观察","v":"opt","terr":0,"ord":45,"grp":"sandgoby","note":"可替换黄守望位；要找食物及照顾砂面，确认吃人工饵；防跳。"},
{id:"new_sexgutt",cn:"蓝点白虾虎",sci:"Valenciennea sexguttata","len":14.0,"cm":"最大记录14（全长）","zone":"底层","col":"白身蓝色面点","tem":"视个体及同伴","coral":"视物种与个体","shrimp":"一般需观察","v":"temp","terr":0,"ord":45,"grp":"sandgoby","note":"可替换黄守望位；翻砂会扬砂，成熟砂床与补喂需落实，幼鱼过渡或后续空间。"},
{id:"new_huchtii",cn:"绿宝石",sci:"Pseudanthias huchtii","len":12.0,"cm":"最大记录12（全长）","zone":"中层","col":"粉紫橙色调","tem":"视个体及同伴","coral":"视物种与个体","shrimp":"一般需观察","v":"opt","terr":0,"ord":45,"grp":"anthias","note":"可替换中层鱼位（需调整组合）；需要多次小餐和足够游泳空间，先确认开口。"},
{id:"new_pulcher",cn:"紫红宝石",sci:"Pseudanthias pulcherrimus","len":7.0,"cm":"最大记录7（标准体长，不含尾鳍）","zone":"中层","col":"红紫色宝石鱼","tem":"视个体及同伴","coral":"视物种与个体","shrimp":"一般需观察","v":"opt","terr":0,"ord":45,"grp":"anthias","note":"可替换中层鱼位（需调整组合）；标准体长不含尾鳍；需多次小餐和稳定开口。"},
{id:"new_rubrizon",cn:"三色宝石",sci:"Pseudanthias rubrizonatus","len":12.0,"cm":"最大记录12（全长）","zone":"中层","col":"橙粉色带纹","tem":"视个体及同伴","coral":"视物种与个体","shrimp":"一般需观察","v":"opt","terr":0,"ord":45,"grp":"anthias","note":"可替换中层鱼位（需调整组合）；需要多次小餐和开阔水域；先确认开口。"},
{id:"new_evanidus",cn:"蒙娜丽莎狐",sci:"Pseudocheilinus evanidus","len":9.0,"cm":"最大记录9（全长）","zone":"中层","col":"橙红身细白线","tem":"视个体及同伴","coral":"视物种与个体","shrimp":"小型无脊椎需留意","v":"opt","terr":0,"ord":45,"grp":"other","note":"可替换中层鱼位（需调整组合）；较隐蔽，会吃小型底栖无脊椎；防跳并观察小虾。"},
{id:"new_flaviver",cn:"日出龙",sci:"Pseudochromis flavivertex","len":7.2,"cm":"最大记录7.2（全长）","zone":"洞穴","col":"蓝紫身黄色背部","tem":"视个体及同伴","coral":"视物种与个体","shrimp":"一般需观察","v":"opt","terr":1,"ord":45,"grp":"cave","note":"可替换蓝鬼王位；有守洞性，可能追逐雷达或小型洞栖鱼；留退避处。"},
{id:"new_aureus",cn:"环尾玫瑰",sci:"Ostorhinchus aureus","len":14.5,"cm":"最大记录14.5（全长）","zone":"中层","col":"银灰身和尾柄黑环","tem":"视个体及同伴","coral":"视物种与个体","shrimp":"一般需观察","v":"opt","terr":0,"ord":45,"grp":"apogon","note":"可替换中层鱼位（需调整组合）；成体较大，需准备后续空间；喂细肉食。"},
{id:"new_dispar",cn:"紫罗兰宝石",sci:"Nemanthias dispar","len":9.5,"cm":"最大记录9.5（全长）","zone":"中层","col":"粉橙身、黄尾","tem":"视个体及同伴","coral":"视物种与个体","shrimp":"一般需观察","v":"opt","terr":0,"ord":45,"grp":"anthias","note":"可替换中层鱼位（需调整组合）；需多次小餐和活动空间；单条饲养状态需观察。"},
{id:"new_bartlett",cn:"夏威夷宝石",sci:"Nemanthias bartlettorum","len":9.0,"cm":"最大记录9（全长）","zone":"中层","col":"紫红身黄色背部","tem":"视个体及同伴","coral":"视物种与个体","shrimp":"一般需观察","v":"opt","terr":0,"ord":45,"grp":"anthias","note":"可替换中层鱼位（需调整组合）；需多次小餐和活动空间，可能与同类争斗。"},
{id:"new_multif",cn:"十一间仙",sci:"Centropyge multifasciata","len":12.0,"cm":"最大记录12（全长）","zone":"巡游","col":"白身细黑竖纹","tem":"视个体及同伴","coral":"谨慎：可能啄珊瑚","shrimp":"一般需观察","v":"no","terr":1,"ord":45,"grp":"angel","note":"可替换小型仙位（三选一）；较难开口，空检疫桶容易缺少可觅食石面；可能啄珊瑚，先确认持续进食并准备岩洞；资料记载常有饥饿，现阶段不建议。"},
{id:"new_bimac",cn:"黄糖果狐",sci:"Bodianus bimaculatus","len":5.9,"cm":"最大记录5.9（标准体长，不含尾鳍）","zone":"中层","col":"黄橙身带红纹","tem":"视个体及同伴","coral":"视物种与个体","shrimp":"小型无脊椎需留意","v":"opt","terr":0,"ord":45,"grp":"other","note":"可替换中层鱼位（需调整组合）；标准体长不含尾鳍；初入可能难开口，可能捕食小型无脊椎，注意小虾。"},
{id:"new_sycorax",cn:"金翅火麒麟",sci:"Synchiropus sycorax","len":4.0,"cm":"最大记录4（标准体长，不含尾鳍）","zone":"底层","col":"红色底白纹，鳍色艳","tem":"视个体及同伴","coral":"视物种与个体","shrimp":"一般需观察","v":"no","terr":0,"ord":45,"grp":"mand","note":"可替换黄守望位；依赖细小底栖食物，新缸食物不足易消瘦；本缸不接种桡足类，现阶段不建议，成熟后只考虑已稳定吃替代饵的个体。"},
];
// 线下店报价：上海天晴之海报价单（用户提供，2026-10-29）原样摘录；c=商品名对应关系需到店确认；b=单条基础价，用于组合合计
const STORE_DATE="2026-10-29";
const STORE={
 watch:{l:["黄金虾虎 s 50","黄金虾虎 ss 59/2条"],b:50},
 fire:{l:["红雷达 45/条","120/3条"],b:45},
 para:{l:["黄尾蓝魔 28/条","100/4条"],b:28},
 gramma:{l:["双色鬼王（人）ss 240","s 260"],b:240,c:1},
 clown:{l:["宿务公子 3cm 35","4cm 45","巴厘岛公子 4+ 80起","特大公子 7–9 160"],b:35},
 kath:{l:["凯瑟琳雀 公 6+ 240"],b:240,c:1},
 herald:{l:["黄新娘 7− 80","7+ 90"],b:80},
 bisp:{l:["蓝闪电 5–7 80"],b:80},
 bicang:{l:["石美人 bb5− 49"],b:49},
 flame:{l:["火焰仙 420起"],b:420},
 ytang:{l:["大黄吊 9+ 200起"],b:200,c:1},
 btang:{l:["蓝吊 10+ 300起"],b:300},
 sail:{l:["大帆吊 6–8 95","8–10 110"],b:95},
 fox:{l:["黄狐狸 6–7 140","…11–12 220"],b:140},
 french:{l:["法仙 8–9 1750"],b:1750}
};
const MALL=(window.FISH_MALL||{}).by||{},MALL_DATE=(window.FISH_MALL||{}).d||"";
const spec=x=>!x?"规格未写":/^\d+(\.\d+)?\+$/.test(x)?x.slice(0,-1)+"cm以上":/^\d+(\.\d+)?-$/.test(x)?x.slice(0,-1)+"cm以下":/^\d+(\.\d+)?~\d+(\.\d+)?$/.test(x)?x.replace("~","–")+"cm":/^\d+(\.\d+)?$/.test(x)?x+"cm":x;
const AQ=window.FISH_AQ||{};
const esc=s=>String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
function priceHTML(id){
  const st=STORE[id],m=MALL[id];let h="";
  if(m){const b=m.best.map(([p,z,s,loc,up,nt])=>`${p}元 ${spec(z)}·${s}（${loc}，鱼单${up}更新${nt?"，"+nt:""}）`).join("；");
    h+=`<div class="pr"><span class="src">水族名录</span><span>${m.k?`近期鱼单列有库存：${esc(b)}`:"暂无近期明确库存记录"}。共${m.s}家店${m.n}个规格，${m.lo}–${m.hi}元 <em>${MALL_DATE}拉取，不含运费；库存以店家为准</em>${m.u.map(u=>` <a href="${esc(u)}" target="_blank" rel="noopener">物种页</a>`).join("")}<details><summary>查看各店全部报价</summary>${m.rows.map(([p,z,s,loc,up,stock,name,note])=>`<div>${esc(s)}（${esc(loc)}） · ${esc(name)} · ${esc(spec(z))} · ${esc(p)}元 · 库存${esc(stock||"未填写")} · 鱼单${esc(up)}${note?` · ${esc(note)}`:""}</div>`).join("")}</details></span></div>`}
  if(st)h+=`<div class="pr"><span class="src">天晴之海</span><span>${st.l.join("；")}${st.c?' <em>名称待到店确认</em>':""} <em>报价单${STORE_DATE}</em></span></div>`;
  return h||`<div class="pr"><span class="src">价格</span><span class="mut">本次鱼单未匹配到报价</span></div>`;
}
const VL={ok:"优先候选",opt:"条件候选",temp:"过渡候选",no:"另配方案"};
const VC={ok:"var(--ok)",opt:"var(--opt)",temp:"var(--temp)",no:"var(--no)"};
const ZONES=["底层","停栖","洞穴","中下层","中层","巡游"];
const PRESETS=[
 {n:"我们的清单",p:{watch:1,citr:1,fire:1,tomi:1,btang:1,macn:1,bisp:1,clown:2,para:1}},
 {n:"你的18条（原选）",p:{watch:1,yasha:1,citr:1,atrod:1,fire:1,dart:1,cyano:1,macn:1,assess:1,melan:1,herald:1,aura:1,clown:2,gramma:1,hemi:1,allen:1,para:1}},
 {n:"精选10条（建议）",p:{watch:1,citr:1,fire:1,dart:1,atrod:1,macn:1,herald:1,clown:2,para:1}},
 {n:"稳妥6条",p:{clown:2,watch:1,fire:1,gramma:1,para:1}},
 {n:"想要吊·8条",p:{watch:1,okin:1,fire:1,tomi:1,clown:2,gramma:1,para:1}},
 {n:"黄三角过渡",p:{watch:1,fire:1,ytang:1,clown:2,para:1}},
 {n:"火焰仙主角",p:{watch:1,fire:1,flame:1,clown:2,para:1}},
 {n:"全温和不打架",p:{watch:1,okin:1,fire:1,pajama:1,assess:1,flash:1,clown:2}},
 {n:"中层热闹",p:{watch:1,fire:1,flash:1,pink:1,clown:2,para:1}},
 {n:"蓝黄不打架",p:{watch:1,fire:1,atrod:1,macn:1,kath:1,clown:2}},
 {n:"黄色系·黄新娘",p:{watch:1,okin:1,assess:1,herald:1,clown:2}}
];
const TANK=58.4;
const byId=Object.fromEntries(F.map(f=>[f.id,f]));
let pick={};
try{const s=JSON.parse(localStorage.getItem("fishpick")||"null");if(s&&typeof s==="object")pick=s}catch(e){}
if(!Object.keys(pick).length)pick={...PRESETS[0].p};
const save=()=>{try{localStorage.setItem("fishpick",JSON.stringify(pick))}catch(e){}};

const SLOTS=[
 {n:"底层砂洞",ids:["watch","yasha"]},{n:"停在石头上的小虾虎",ids:["citr","okin","histrio"]},{n:"中层悬停",ids:["fire"]},
 {n:"主角位（第一条吊）",ids:["tomi"],w:"便宜温和的吊，过渡养，长到约10cm转出"},{n:"第二条吊（暂定）",ids:["btang"],w:"紧跟火箭吊之后单独一轮，检疫看满30天"},{n:"守石洞",ids:["macn","gramma","assess"]},
 {n:"小型仙（只买1条）",ids:["bisp","herald","flame","new_fisheri"],w:"四条互为备选，可能啃纽扣；火背仙已按审美撤出"},{n:"小丑",ids:["clown"],q:2},{n:"雀鲷，最后入缸",ids:["para","hemi","allen"]}];
const CREW=[
 {id:"c_pistol",cn:"虎纹枪虾",sci:"Alpheus bellulus",k:2,q:"1只",when:"W0，和螺同一批",role:"和黄守望共用一个洞：枪虾挖洞，虾虎站岗",note:"黄守望的配对伙伴，比黄守望早一轮进缸先挖洞。窝后约200×150mm的砂堆到50～60mm给它挖隧道。另外少量补喂。配对不一定成功，不成功也不打架。滴流过水。",pr:"水族名录两家65–70（11-05都缺货）"},
 {id:"c_nass",cn:"织纹螺",sci:"Nassarius 类",k:1,q:"2只",when:"W0，同一批",role:"钻砂、吃沉底残饵",note:"靠鱼餐残饵吃饱，饿死会坏水。只买海水水族用小型款。",pr:""},
 {id:"c_troch",cn:"清洁螺（马蹄螺）",sci:"Trochidae，Tectus／Trochus 类，看实物",k:1,q:"3只，藻多再加2～3",when:"W0，同一批",role:"刮玻璃和石面藻膜",note:"英文论坛评价最好的刮藻螺：翻倒能自己翻回来，会在缸里繁殖。小螺可能被吸进泵，底缸泵格进水口套网。前两个月没藻时夹海苔喂。",pr:"水族名录 浩奇 4"},
 {id:"c_cerith",cn:"塔螺",sci:"多为 Cerithium 类，看实物",k:1,q:"3只，藻多再加2～3",when:"W0，同一批",role:"石面、砂面藻膜和碎屑",note:"买小个的，大螺会推倒珊瑚。",pr:"天晴之海 8"},
 {id:"c_cowry",cn:"金环宝螺",sci:"Monetaria annulus",k:1,q:"2只",when:"W0，同一批",role:"夜间啃藻",note:"约2–3cm，能自己翻身。会推倒没粘牢的小苗，珊瑚要粘稳。没藻时吃海苔。",pr:"天晴之海 5；鱼嬉海洋 5只15"},
 {id:"c_urchin",cn:"蓝礼服海胆",sci:"Mespilia globulus",k:1,q:"1只",when:"W0，同一批",role:"夜里啃石面藻，背碎壳当伪装",note:"成体约7.5cm。会背碎壳和没粘牢的小苗，也会啃粉色珊瑚藻；论坛有拔纽扣的记录，纽扣粘牢塞进石缝。前两个月每周3次傍晚夹海苔、早上取出。怕铜药和高NO3，滴流过水。",pr:"水族名录 瀚洋水族 56（陕西，11-05有7只）"},
 {id:"c_clean",cn:"医生虾",sci:"Lysmata amboinensis",k:1,q:"1只",when:"W0，同一批",role:"清理鱼体表、吃残饵",note:"放在石下阴影处，蜕壳时要有躲的地方。和清单里的鱼都能混养。滴流过水。",pr:"天晴之海 120起"},
 {id:"c_fire",cn:"火焰虾",sci:"Lysmata debelius",k:0,q:"1只",when:"鱼都稳定后，可选",role:"也清理鱼体表，主要是好看",note:"深红配白点，白天多在石洞里。会把医生虾赶出洞，两只要各有藏身处。",pr:"天晴之海 120起"}
];

const IMGB=(window.SITE_BASE||"")+"img/";
const BATCHES=[
 {n:"小丑",when:"检疫桶通过后入桶，W0转主缸",ids:[["clown",2]],note:"入桶至少14天、目标30天；主缸两轮检查通过后才转。"},
 {n:"第1轮",when:"W0入桶，约W2～4转主缸",ids:[["watch",1],["fire",1]],note:"天晴之海买。黄守望放在枪虾洞附近。"},
 {n:"第2轮",when:"约W2～4入桶，约W4～8转主缸",ids:[["citr",1],["macn",1]],note:"淘宝一单。蛋分装好、稳定出沫约1周才转主缸。"},
 {n:"第3轮",when:"约W4～8入桶，约W6～12转主缸",ids:[["tomi",1]],note:"单独一轮，买5～7cm，每周换水2次；长到约10cm转给更大的缸。"},
 {n:"第4轮",when:"约W6～12入桶，满30天转主缸",ids:[["btang",1]],note:"暂定。单独一轮，买得和火箭吊一样大或略大；容易白点，看满30天。"},
 {n:"第5轮",when:"纽扣入缸后",ids:[["bisp",1]],note:"小型仙只买1条：蓝闪电、黄新娘、火焰仙、渔夫仙互为备选，买时看哪条状态最好。入缸后两周看是否啄纽扣。"},
 {n:"第6轮",when:"小型仙转主缸后",ids:[["para",1]],note:"单独一轮。雀鲷最后进缸，观察追咬和堵洞。"}];
const short=s=>s.split("（")[0];
function shortPrice(id){const m=MALL[id],st=STORE[id];return m?["水族名录",m.k?`${m.best[0][0]}元起（鱼单列有库存）`:`${m.lo}–${m.hi}元（库存待核）`]:st?["天晴之海",st.l[0]]:["",""]}
function figOf(id,alt){const im=IMG[id];return im?`<figure><img src="${IMGB}${im.f}" alt="${alt}" loading="lazy" data-zi="${id}" data-zn="${alt}"><figcaption>${im.a}</figcaption></figure>`:`<figure class="noimg">暂无照片</figure>`}
function priceLine(id){const [w,p]=shortPrice(id);return w?`<div class="store">${esc(w)} <b class="price">${esc(p)}</b></div>`:`<div class="store">本次鱼单未匹配到报价</div>`}

function renderHome(){
 const bt=document.getElementById("batches");
 if(bt)bt.innerHTML=BATCHES.map(b=>`<article class="batch"><div class="bn"><b>${b.n}</b><span>${b.ids.reduce((s,x)=>s+x[1],0)}条</span></div>
  <div class="when">${b.when}</div>
  <ul>${b.ids.map(([id,q])=>{const f=byId[id],im=IMG[id];return `<li>${im?`<img src="${IMGB}${im.f}" alt="">`:`<img alt="">`}${short(f.cn)}<small>×${q}</small></li>`}).join("")}</ul>
  <div class="bnote">${b.note}</div></article>`).join("");
 const sl=document.getElementById("slots");
 if(sl)sl.innerHTML=SLOTS.map((s,i)=>{const f=byId[s.ids[0]],aq=AQ[f.id];
  const alts=s.ids.slice(1).map(a=>{const g=byId[a],im=IMG[a],[w,p]=shortPrice(a);return `<span class="alt">${im?`<img src="${IMGB}${im.f}" alt="">`:""}${short(g.cn)}${p?` · ${p}`:""}</span>`}).join("");
  return `<article class="cardx">${figOf(f.id,f.cn)}<div class="bd">
  <div class="pos"><span class="no">${String(i+1).padStart(2,"0")}</span>${s.n}<span class="qty">${s.q||1}条</span></div>
  <div class="pick">${short(f.cn)}</div>
  ${aq?`<div class="store">店里叫 <b>${aq.main}</b></div>`:""}
  ${priceLine(f.id)}
  ${s.w?`<div class="hint">${s.w}</div>`:""}
  ${alts?`<div class="alts"><span class="lab">买不到首选时，换同一位置的备选</span>${alts}</div>`:""}</div></article>`}).join("");
 const cg=document.getElementById("crewgrid");
 if(cg)cg.innerHTML=CREW.map(c=>`<article class="cardx">${figOf(c.id,c.cn)}<div class="bd">
  <div class="pos"><span class="tag ${c.k===1?"core":c.k===2?"user":"opt"}">${c.k===1?"基础":c.k===2?"已确认":"可选"}</span><span class="qty">${c.q}</span></div>
  <div class="pick">${c.cn}</div><div class="sci">${c.sci}</div>
  <dl class="kv"><dt>何时</dt><dd>${c.when}</dd><dt>作用</dt><dd>${c.role}</dd>${c.pr?`<dt>报价</dt><dd>${c.pr}</dd>`:""}</dl>
  <div class="note">${c.note}</div>
  ${c.alt?`<div class="alts"><span class="lab">也可以换成</span><span class="alt">${IMG[c.alt.id]?`<img src="${IMGB}${IMG[c.alt.id].f}" alt="">`:""}${c.alt.cn} · ${c.alt.pr}</span></div>`:""}</div></article>`).join("");
}

function card(f){
  const n=pick[f.id]||0,pct=Math.min(100,f.len/TANK*100);
  const im=IMG[f.id];
  const fig=im?`<figure><img src="${IMGB}${im.f}" alt="${f.cn}照片" loading="lazy" data-z="${f.id}"><figcaption>${im.a}</figcaption></figure>`:`<figure class="noimg">暂无照片</figure>`;
  return `<article class="cat-card${n?" sel":""}">${fig}<div class="bd">
  <div class="ctop"><div style="min-width:0"><div class="cname">${f.cn}${f.liked?'<span class="liked">你提过</span>':""}${f.id.startsWith("new_")?'<span class="isnew">新加</span>':""}</div><div class="sci">${f.sci}</div></div>
  <span class="pill v-${f.v}">${VL[f.v]}</span></div>
  ${AQ[f.id]?`<div class="tn">店里常叫 <b>${AQ[f.id].main}</b>${AQ[f.id].alt.length?"，也叫"+AQ[f.id].alt.slice(0,3).join("、"):""} <a href="${AQ[f.id].u}" target="_blank" rel="noopener">水族名录↗</a></div>`:""}
  <div class="size"><div class="bar"><i style="width:${pct}%;background:${VC[f.v]}"></i></div><small>成体 ${f.cm} cm · 占缸长 ${Math.round(pct)}%</small></div>
  <dl><dt>活动</dt><dd>${f.zone}</dd><dt>颜色</dt><dd>${f.col}</dd><dt>性格</dt><dd>${f.tem}</dd><dt>珊瑚</dt><dd>${f.coral}</dd><dt>虾</dt><dd>${f.shrimp}</dd></dl>
  <div class="note">${f.note}</div>
  <div class="prices">${priceHTML(f.id)}</div>
  <div class="act"><a href="https://www.bing.com/images/search?q=${encodeURIComponent(f.sci.split(/[（(]/)[0].trim())}" target="_blank" rel="noopener">更多图片 ↗</a>
  ${/^[A-Z][a-z]+ [a-z]+$/.test(f.sci)?`<a href="https://www.fishbase.se/summary/${encodeURIComponent(f.sci.replace(' ','-'))}.html" target="_blank" rel="noopener">FishBase ↗</a>`:""}
  ${n?`<button class="btn ghost" data-a="${f.id}" data-d="-1">移出（${n}）</button>`:`<button class="btn" data-a="${f.id}" data-d="1">${f.unit?"加入一对":"加入"}</button>`}</div>
  </div></article>`
}

function check(){
  const ids=Object.keys(pick),W=[],fs=ids.map(i=>byId[i]);
  const N=ids.reduce((s,i)=>s+pick[i],0);
  const terr=ids.reduce((s,i)=>s+byId[i].terr*(byId[i].unit?1:pick[i]),0);
  const L=ids.reduce((s,i)=>s+byId[i].len*pick[i],0);
  const g={};fs.forEach(f=>{g[f.grp]=(g[f.grp]||0)+(f.unit?pick[f.id]/f.unit:pick[f.id])});
  const has=x=>!!pick[x];
  fs.filter(f=>f.v==="no").forEach(f=>W.push(["no",`${f.cn}需要另配饲养方案：${f.note}`]));
  if(g.tang>2)W.push(["no","吊超过2条：论坛60缸里养3～4条吊的多数出过死鱼、追打或白点，最多2条。"]);
  else if(g.tang===2)W.push(["opt","2条吊：60缸里最常见的养法，但吊之间可能追打。两条买得差不多大、紧挨着进缸，长大或持续追打时转出一条。"]);
  if(g.angel>1)W.push(["no","小型仙全缸只能1条。"]);
  if(g.clown>1)W.push(["no","小丑只养一对，不要第二对或混其他小丑。"]);
  if(g.lion&&(N>pick[fs.find(f=>f.grp==="lion").id]))W.push(["no","狮子鱼、枯叶鱼这类伏击鱼会吞食能入口的鱼虾；需按成年口裂和同伴体型另配方案，当前小鱼、清洁虾组合不合适。"]);
  if(g.damsel>1)W.push(["opt","两条雀鲷在60缸容易互斗，留1条。"]);
  if(g.cave>1)W.push(["opt","草莓类守同一种洞穴，只选1条。"]);
  if(g.firefish>1)W.push(["opt","雷达类非配对会互斗，只养1条。"]);
  if(g.gobiodon>1)W.push(["opt","蟋蟀类小虾虎会抢停栖点，只选1条。"]);
  if(g.blenny>1)W.push(["opt","鳚类会抢石洞，只选1条。"]);
  if(g.flasher>1)W.push(["opt","闪光/仙女隆头只养1条公鱼。"]);
  if(g.sandgoby>1)W.push(["opt","底栖砂洞虾虎只放1条。"]);
  if(has("sixl")&&["fire","deco","pink","flash","fairy","possum","assess"].some(has))W.push(["opt","六线龙会欺负组合里胆小的温和鱼，二者择一。"]);
  if(has("frid")||has("pacc"))if(["fire","deco","pink","assess"].some(has))W.push(["opt","这款草莓会压制雷达、粉红条纹龙等胆小鱼，换成皇家草莓更稳。"]);
  if(g.angel)W.push(["opt","小型仙可能啃纽扣：纽扣粘在可取出的小石上，入缸后观察两周，持续啃就移走纽扣。"]);
  fs.filter(f=>f.v==="temp").forEach(f=>W.push(["opt",`${f.cn}按幼鱼过渡评估：购前落实更大主缸或接手去处，结合体长增长及巡游、领地提前安排转出；不承诺固定可养年限。`]));
  if(has("mand"))W.push(["opt","青蛙要等开缸一年后、且只买已吃冻饵的个体。"]);
  if(g.tang&&g.damsel)W.push(["ok","吊要在雀鲷之前入缸，下面顺序已按此排。"]);
  if(N>10)W.push(["opt",`共${N}条，数量较多；需结合成年体型、活动区域、领地和日常负荷复核，不能只按条数决定。`]);
  else if(N>8)W.push(["opt",`共${N}条，偏多：前提是每周换水约10%、蛋分常开，且最后几条等全缸稳定2–3个月再加。`]);
  if(terr>=7)W.push(["opt",`守域分${terr}偏高，地盘鱼太多，追咬风险大。减一条守域鱼。`]);
  if(["watch","fire","deco","flash","fairy","atrod","oual","gram","btang","tomi","new_yanoi","new_guttata","new_bella","new_sexgutt","new_huchtii","new_pulcher","new_rubrizon","new_dispar","new_bartlett"].some(has))W.push(["ok","组合里有会跳的鱼：缸上要有防跳措施（围板或盖网，还没定）。"]);
  if(N&&!W.some(w=>w[0]!=="ok"))W.unshift(["ok","没有发现冲突，这个组合可以用。"]);
  return {N,terr,L,W}
}

let fv="all",fz="all",fl=false,fn=false,q="";
function chips(el,opts,get,set){
  opts.forEach(([k,l])=>{const b=document.createElement("button");b.className="chip";b.textContent=l;b.dataset.k=k;
    b.onclick=()=>{set(k);render()};el.appendChild(b)});
  el._sync=()=>el.querySelectorAll(".chip").forEach(b=>b.setAttribute("aria-pressed",b.dataset.k===get()))
}
function add(id,d){const f=byId[id];const u=f.unit||1;pick[id]=Math.max(0,(pick[id]||0)+d*u);if(!pick[id])delete pick[id];save();render()}
function render(){
  if(!document.getElementById("grid"))return;
  ["fv","fz"].forEach(i=>document.getElementById(i)._sync());
  document.getElementById("fl").setAttribute("aria-pressed",fl);
  document.getElementById("fn").setAttribute("aria-pressed",fn);
  const list=F.filter(f=>(fv==="all"||f.v===fv)&&(fz==="all"||f.zone===fz)&&(!fl||f.liked)&&(!fn||f.id.startsWith("new_"))&&(!q||(f.cn+f.sci+(AQ[f.id]?AQ[f.id].main+AQ[f.id].alt.join(''):'')).toLowerCase().includes(q)));
  document.getElementById("grid").innerHTML=list.map(card).join("")||'<p class="empty">没有符合条件的鱼，换个筛选试试。</p>';
  document.getElementById("cnt").textContent=`${list.length} / ${F.length} 种`;
  const {N,terr,L,W}=check();
  document.getElementById("sN").textContent=N;document.getElementById("sT").textContent=terr;document.getElementById("sL").textContent=Math.round(L);

  const ids=Object.keys(pick).sort((a,b)=>byId[a].ord-byId[b].ord);
  document.getElementById("picks").innerHTML=ids.length?ids.map(i=>`<li><span>${short(byId[i].cn)} <span class="pill v-${byId[i].v}">${VL[byId[i].v]}</span></span>
   <span class="qtyc"><button aria-label="减少" data-a="${i}" data-d="-1">−</button>${pick[i]}<button aria-label="增加" data-a="${i}" data-d="1">+</button></span></li>`).join(""):'<li class="empty" style="list-style:none;margin-left:-1.4em">还没选鱼。点上面的现成组合，或在目录里点“加入”。</li>';
  document.getElementById("warns").innerHTML=W.map(([k,t])=>`<li class="w-${k}">${t}</li>`).join("")||'<li class="empty">选鱼后这里显示检查结果。</li>';
}
function initCatalog(){
  if(!document.getElementById("grid"))return;
  chips(document.getElementById("fv"),[["all","全部"],["ok","优先候选"],["opt","条件候选"],["temp","过渡候选"],["no","另配方案"]],()=>fv,k=>fv=k);
  chips(document.getElementById("fz"),[["all","全部"],...ZONES.map(z=>[z,z])],()=>fz,k=>fz=k);
  document.getElementById("fl").onclick=()=>{fl=!fl;render()};
  document.getElementById("fn").onclick=()=>{fn=!fn;render()};
  document.getElementById("q").oninput=e=>{q=e.target.value.trim().toLowerCase();render()};
  document.getElementById("clear").onclick=()=>{pick={};save();render()};
  const pr=document.getElementById("presets");
  PRESETS.forEach(p=>{const b=document.createElement("button");b.className="chip";b.textContent=p.n;b.onclick=()=>{pick={...p.p};save();render()};pr.appendChild(b)});
  render();
}
document.addEventListener("click",e=>{
  const z=document.getElementById("zoom");if(z&&e.target.closest("#zoom")){z.remove();return}
  const zi=e.target.closest("[data-zi]");
  if(zi){const im=IMG[zi.dataset.zi];const d=document.createElement("div");d.id="zoom";d.innerHTML=`<div><img src="${IMGB}${im.f}" alt=""><p>${zi.dataset.zn}<br>${im.a}</p></div>`;document.body.appendChild(d);return}
  const i=e.target.closest("[data-z]");
  if(i){const f=byId[i.dataset.z],im=IMG[f.id];const d=document.createElement("div");d.id="zoom";
    d.innerHTML=`<div><img src="${IMGB}${im.f}" alt="${f.cn}"><p>${f.cn} · ${f.sci}<br>${im.a}</p></div>`;document.body.appendChild(d);return}
  const b=e.target.closest("[data-a]");if(b)add(b.dataset.a,+b.dataset.d)});
document.addEventListener("keydown",e=>{if(e.key==="Escape")document.getElementById("zoom")?.remove()});
renderHome();
initCatalog();
