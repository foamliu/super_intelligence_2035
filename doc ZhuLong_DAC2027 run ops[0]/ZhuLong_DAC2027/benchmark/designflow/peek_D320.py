#!/usr/bin/env python3
"""Peek batch for shard D #320. Run ON .75. Parallel ssh to target machines.
Directory-based cline storage: /home/<user>/.cline/data/sessions/<sid>/<sid>.messages.json
Extract user turns + assistant tool signal (editor + produce files) to triage A-faithful produce candidates.
"""
import json, subprocess, concurrent.futures, re, sys
TARGETS = [
    ('1792995706498_jsb4j', 'yohannw', '10.129.2.12', 196, 'virtuoso:837;cellview:233;schematic:157;cadence:106;pyaether:33;analog:28;ddgetobj:23;aether:15;'),
    ('1782890212076_npkmm', 'e0031982', '10.129.32.75', 193, 'aether:266;virtuoso:101;analog:93;pyaether:63;dbcreateinst:8;dbcreatepath:7;dbcreaterect:6;cellview:2;'),
    ('1793165432787_o5o6p', 'e0046913', '10.129.2.12', 184, 'synopsys:2213;netlist:202;pyaether:20;aether:13;virtuoso:6;cadence:6;spectre:1;schematic:1;'),
    ('1790236401918_27c6f', 'jason17w', '10.129.32.190', 166, 'netlist:581;synopsys:168;hspice:72;skipper:50;aether:28;calibre:22;cadence:4;analog:3;'),
    ('1791611132079_5vmvu', 'ellawu', '10.129.2.14', 165, 'dbcreatelabel:532;schematic:315;cellview:106;dbget:55;.cdl:40;ddgetobj:22;dbopencellviewbytype:22;aether:13;'),
    ('1789913077711_ld0p8', 'ziyuny', '10.129.32.190', 164, 'cmos:721;calibre:427;netlist:129;.spi:76;aether:66;schematic:44;.cdl:44;.gds:32;'),
    ('1791967362296_kxqt7', 'yzwang', '10.129.2.10', 162, 'pdk:306;calibre:298;analog:67;.def:27;pyaether:5;cmos:5;.gds:5;aether:4;'),
    ('1791958893585_o4frj', 'yzwang', '10.129.2.10', 161, 'pdk:307;calibre:299;analog:67;.def:27;pyaether:5;cmos:5;.gds:5;aether:4;'),
    ('1790652004587_8zuqr', 'mike', '10.129.32.80', 161, 'synopsys:288;aether:42;cadence:26;pyaether:19;schematic:8;hspice:7;analog:5;cellview:4;'),
    ('1789961467130_nibwl', 'ziyuny', '10.129.32.190', 154, 'aether:598;cellview:187;schematic:131;pyaether:72;analog:60;dbopencv:54;cmos:53;lib.defs:46;'),
    ('1785390178118_ewjnc', 'e0014566', '10.129.2.10', 147, 'cellview:216;pyaether:145;aether:102;dbget:67;virtuoso:59;schematic:38;dbopencellviewbytype:34;synopsys:33;'),
    ('1792738287471_mrlo9', 'e03179', '10.129.2.11', 144, 'netlist:460;analog:190;transistor:97;synopsys:96;schematic:60;waveview:38;opamp:13;mosfet:13;'),
    ('1786710801484_wsi93', 'e0014566', '10.129.2.10', 143, 'cellview:264;pyaether:99;dbget:81;dbopencellviewbytype:68;virtuoso:60;analog:58;dbopencv:37;netlist:26;'),
    ('1785899794656_0j59o', 'michael1l', '10.129.2.12', 143, 'cellview:183;virtuoso:133;cadence:129;pyaether:128;aether:76;floorplan:74;schematic:28;dbcreateinst:24;'),
    ('1790131515178_j90k2', 'e0045291', '10.129.8.120', 139, 'schematic:245;pyaether:55;opamp:14;aether:10;cmos:8;analog:7;netlist:6;cellview:6;'),
    ('1792043637880_ajcab', 'e0023936', '10.129.32.75', 138, 'pyaether:258;schematic:226;cellview:116;aether:29;netlist:18;dbshape:10;dbopencv:4;dbget:4;'),
    ('1791792980970_4vv1y', 'lizwen', '10.129.2.11', 138, 'aether:597;cellview:251;dbget:84;pyaether:81;calibre:56;schematic:55;dbcreateinst:46;mixed-signal:42;'),
    ('1792140744683_z5ett', 'jessegao', '10.129.2.14', 137, 'aether:512;transistor:224;pdk:169;netlist:129;schematic:99;pyaether:91;calibre:37;dbopencv:25;'),
    ('1792142998625_n1njg', 'jessegao', '10.129.2.14', 137, 'aether:512;transistor:224;pdk:169;netlist:129;schematic:99;pyaether:91;calibre:37;dbopencv:25;'),
    ('1786586471140_pepxy', 'e0014566', '10.129.2.10', 137, 'virtuoso:522;analog:113;.gds:71;cellview:60;calibre:57;dbopencellviewbytype:26;cadence:24;dbcreatelabel:17;'),
    ('1790684140804_vtl11', 'haoliu', '10.129.8.106', 135, 'synopsys:379;waveview:276;hspice:33;schematic:31;cellview:30;netlist:24;mosfet:13;techfile:8;'),
    ('1792659994477_rw6z4', 'e0045488', '10.129.2.11', 134, '.spi:450;pdk:138;hspice:40;synopsys:32;netlist:32;aether:13;pyaether:12;cadence:11;'),
    ('1792993323406_1488k', 'rayfeng', '10.129.2.10', 133, 'synopsys:331;waveview:136;dbget:80;aether:51;.gds:49;gdsii:44;bandgap:41;.lef:36;'),
    ('1786613295407_a9ta2', 'e0014566', '10.129.2.10', 131, 'cellview:406;analog:226;pyaether:103;dbopencellviewbytype:57;floorplan:36;virtuoso:35;netlist:34;aether:26;'),
    ('1791792661412_ibsuq', 'lizwen', '10.129.2.11', 131, 'aether:849;pyaether:129;schematic:44;virtuoso:43;cellview:40;transistor:23;techfile:19;mixed-signal:18;'),
    ('1789470466679_wqxag', 'shaoyou', '10.129.2.13', 130, 'aether:514;analog:274;synopsys:89;schematic:70;skipper:49;.cdl:48;pyaether:41;netlist:40;'),
    ('1790149493569_194wf', 'ziyuny', '10.129.32.190', 128, 'aether:583;schematic:210;analog:126;dbopencv:92;pyaether:53;netlist:31;floorplan:6;dbshape:6;'),
    ('1793062149793_u8ovn', 't0002616', '10.129.2.13', 126, 'netlist:502;aether:329;schematic:234;mixed-signal:126;cellview:96;.def:33;transistor:28;hspice:13;'),
    ('1792668123134_0oeb7', 'colinxu', '10.129.2.18', 124, 'pyaether:159;cellview:72;dbget:55;aether:35;schematic:32;netlist:32;analog:30;dbopencv:29;'),
    ('1791636307671_wiglh', 'jason17w', '10.129.32.190', 123, 'netlist:964;aether:12;lib.defs:8;'),
    ('1793166879135_xs1lj', 'e0017906', '10.129.2.11', 119, 'netlist:324;schematic:12;analog:8;cadence:4;.def:2;'),
    ('1789634880745_4ys8e', 'ellawu', '10.129.2.14', 119, '.gds:2006;calibre:581;aether:285;cadence:113;virtuoso:70;schematic:35;lib.defs:30;techfile:20;'),
    ('1792057192352_iz828', 'shuoran', '10.129.33.28', 116, 'cellview:580;pyaether:318;schematic:190;aether:140;netlist:36;dbget:29;virtuoso:13;waveview:10;'),
    ('1791941283310_41sqh', 'sagequan', '10.129.32.190', 115, 'analog:276;netlist:87;waveview:10;pyaether:4;mosfet:4;mixed-signal:2;lib.defs:2;cadence:2;'),
    ('1791616508124_n52mz', 'yohannw', '10.129.2.12', 115, 'schematic:216;cellview:209;netlist:151;aether:142;virtuoso:76;pyaether:61;dbopencellviewbytype:48;cadence:38;'),
    ('1783422292753_zh4of', 'e0014566', '10.129.2.10', 115, 'virtuoso:412;calibre:124;dbopencellviewbytype:95;.gds:84;dbcreateinst:41;ddgetobj:40;netlist:38;synopsys:24;'),
    ('1786705250400_92ykp', 'e0014566', '10.129.2.10', 114, 'virtuoso:129;cellview:60;dbget:35;dbopencellviewbytype:33;.gds:22;netlist:12;analog:11;dbcreatelabel:6;'),
    ('1789372380761_xxtqb', 'sagequan', '10.129.32.190', 113, 'analog:296;cadence:181;pyaether:3;waveview:2;hspice:2;'),
    ('1791514218543_hkyyj', 't0002962', '10.129.2.12', 112, 'pyaether:518;aether:156;cellview:75;schematic:56;dbopencv:33;dbget:32;netlist:18;lib.defs:16;'),
    ('1782910844277_huntx', 'e0014566', '10.129.2.10', 112, 'virtuoso:235;cellview:80;techfile:29;aether:24;pyaether:19;dbget:19;schematic:12;analog:12;'),
    ('1791532940009_ca92c', 'ziyuny', '10.129.32.190', 108, 'aether:321;schematic:245;cellview:71;dbopencv:65;pyaether:62;.lef:54;analog:47;pdk:38;'),
    ('1791783189298_t2hnp', 'steveny', '10.129.2.11', 108, 'pyaether:720;virtuoso:149;aether:147;cellview:84;schematic:55;netlist:53;cadence:27;dbget:14;'),
    ('1783412272916_uorzd', 'e0014566', '10.129.2.10', 104, 'virtuoso:164;.gds:42;calibre:41;cadence:37;dbopencellviewbytype:32;netlist:24;synopsys:18;hspice:12;'),
    ('1792052564350_a6gif', 'panruan', '10.129.35.69', 103, 'calibre:316;pdk:67;analog:39;pyaether:25;transistor:11;aether:5;cmos:2;gdsii:1;'),
    ('1792053269961_ksa2h', 'panruan', '10.129.35.69', 103, 'calibre:316;pdk:67;analog:39;pyaether:25;transistor:11;aether:5;cmos:2;gdsii:1;'),
    ('1792053423366_xgo8p', 'panruan', '10.129.35.69', 103, 'calibre:316;pdk:67;analog:39;pyaether:25;transistor:11;aether:5;cmos:2;gdsii:1;'),
    ('1792053493233_vhz0j', 'panruan', '10.129.35.69', 103, 'calibre:316;pdk:67;analog:39;pyaether:25;transistor:11;aether:5;cmos:2;gdsii:1;'),
    ('1792053544813_f0yt9', 'panruan', '10.129.35.69', 103, 'calibre:316;pdk:67;analog:39;pyaether:25;transistor:11;aether:5;cmos:2;gdsii:1;'),
    ('1792042544705_d1cg3', 't0002441', '10.129.32.75', 102, 'synopsys:2984;hspice:185;spectre:40;cadence:22;netlist:21;aether:19;pyaether:17;virtuoso:14;'),
    ('1792067800928_1b60m', 'colinxu', '10.129.2.18', 100, 'cellview:537;analog:221;schematic:151;ddgetobj:110;dbopencellviewbytype:104;virtuoso:88;lib.defs:19;aether:14;'),
    ('1789975385741_egm8i', 'davidwu', '10.129.40.209', 98, 'aether:704;schematic:283;pyaether:126;floorplan:124;dbopencv:78;cmos:18;lib.defs:12;synopsys:11;'),
    ('1791787809781_w7un3', 'ziyuny', '10.129.32.190', 96, 'schematic:247;pyaether:76;aether:53;dbget:8;cellview:8;dbopencv:6;lib.defs:5;dbshape:5;'),
    ('1790145633753_pax7g', 'miccao', '10.129.32.47', 93, 'calibre:965;netlist:215;.cdl:81;.gds:58;schematic:57;pdk:37;skipper:27;aether:20;'),
    ('1789889776686_se4uf', 'miccao', '10.129.32.47', 93, '.gds:566;netlist:148;calibre:110;schematic:62;pdk:46;.cdl:43;aether:22;lib.defs:12;'),
    ('1790078872955_vpj8o', 'ziyuny', '10.129.32.190', 93, 'aether:492;schematic:125;analog:72;lib.defs:70;pdk:48;cmos:27;dbopencv:23;pyaether:21;'),
    ('1792112534739_ujxtn', 'gracew', '10.129.2.13', 93, 'netlist:170;cadence:51;schematic:8;analog:7;aether:7;cmos:6;pyaether:4;synopsys:1;'),
    ('1789957560618_7kyrv', 'mike', '10.129.32.80', 92, 'synopsys:1274;analog:47;hspice:40;cadence:12;waveview:6;icc2:4;.def:4;pyaether:3;'),
    ('1791957763339_dhgxy', 'e0039602', '10.129.8.136', 91, 'netlist:202;cadence:4;schematic:3;transistor:2;synopsys:1;pyaether:1;aether:1;'),
    ('1791977055190_ckulq', 'e0045144', '10.129.2.13', 91, 'synopsys:368;schematic:107;netlist:13;synthesis:5;pyaether:3;aether:2;'),
    ('1789636492253_sr1fw', 'miccao', '10.129.32.47', 90, 'calibre:358;analog:153;cmos:119;.gds:21;pdk:9;gdsii:9;bandgap:5;transistor:3;'),
    ('1792548352155_fxcqv', 'hongyuy', '10.129.8.102', 89, 'pyaether:167;netlist:120;dbget:107;schematic:90;hspice:36;cellview:32;calibre:27;dbshape:23;'),
    ('1792135280846_sr426', 'jackliu', '10.129.32.83', 89, 'synopsys:359;netlist:122;cadence:116;skipper:88;hspice:72;calibre:30;aether:30;pyaether:26;'),
    ('1792137921430_3lvd6', 'jackliu', '10.129.32.83', 88, 'synopsys:359;netlist:120;cadence:116;skipper:88;hspice:72;calibre:30;aether:30;pyaether:26;'),
    ('1789115083875_tcqqs', 'sagequan', '10.129.32.190', 88, 'analog:124;.def:82;pyaether:50;synopsys:4;aether:3;waveview:2;netlist:2;hspice:2;'),
    ('1792137924614_tadah', 'jackliu', '10.129.32.83', 87, 'synopsys:359;netlist:118;cadence:116;skipper:88;hspice:72;calibre:30;aether:30;pyaether:26;'),
    ('1792549549929_j0t84', 'zhukaic', '10.129.33.26', 87, 'aether:115;hspice:79;synopsys:29;pdk:27;waveview:25;pyaether:25;netlist:24;mosfet:16;'),
    ('1789730312848_hpd7c', 'yongk1li', '10.129.2.12', 79, 'netlist:364;.gds:55;.cdl:50;transistor:12;virtuoso:2;'),
    ('1790156336826_y2xz6', 'jason17w', '10.129.32.190', 77, 'netlist:324;synopsys:12;hspice:4;aether:4;skipper:3;pyaether:3;calibre:1;'),
    ('1789629900465_d3vay', 'pjli', '172.16.8.13', 77, 'netlist:265;cadence:26;cmos:9;schematic:1;'),
    ('1789631689135_9pcjd', 'miccao', '10.129.32.47', 77, 'techfile:137;schematic:92;.cdl:50;transistor:29;aether:21;netlist:19;lib.defs:18;virtuoso:8;'),
    ('1791456748770_htwv2', 'yzwang', '10.129.2.10', 76, 'netlist:223;calibre:128;pdk:53;.spi:11;.gds:9;gdsii:5;icfb:4;mosfet:3;'),
    ('1793094734633_bn62m', 'han1li', '10.129.35.68', 76, 'virtuoso:1442;calibre:56;schematic:53;netlist:47;.gds:13;.cdl:12;.spi:8;cellview:2;'),
    ('1791515463198_50mu7', 'e0042624', '10.129.2.12', 75, 'aether:881;pdk:159;netlist:98;schematic:93;calibre:80;pyaether:58;lib.defs:48;virtuoso:23;'),
    ('1790663852783_u29lu', 'cwei', '10.129.33.27', 74, 'aether:356;pdk:103;schematic:96;netlist:80;pyaether:68;calibre:35;cmos:19;lib.defs:12;'),
    ('1789386764132_phgjl', 'sagequan', '10.129.32.190', 73, 'analog:156;.def:55;netlist:24;waveview:22;.lef:9;synopsys:4;lib.defs:4;pyaether:3;'),
    ('1783324072633_qidc2', 'e0014566', '10.129.2.10', 73, 'virtuoso:80;cellview:80;.gds:46;calibre:42;netlist:31;dbopencellviewbytype:25;ddgetobj:15;dbcreateinst:5;'),
    ('1789094185350_tze5k', 'sagequan', '10.129.32.190', 72, 'analog:204;cellview:10;.def:9;waveview:4;pyaether:4;netlist:4;hspice:4;.lef:2;'),
    ('1789869595751_0h2bc', 'davidwu', '10.129.40.209', 71, 'schematic:279;floorplan:172;dbopencv:105;aether:95;cellview:92;pyaether:65;calibre:18;lib.defs:6;'),
    ('1793081212647_xyj1z', 'eva1wu', '10.129.35.97', 68, 'aether:344;schematic:211;netlist:96;pyaether:59;pdk:50;lib.defs:26;analog:18;dbget:11;'),
    ('1791612883140_2fb2m', 'ellawu', '10.129.2.14', 68, 'dbcreatelabel:388;schematic:133;cellview:70;dbget:26;ddgetobj:18;dbopencellviewbytype:18;.gds:8;.cdl:8;'),
    ('1789451853998_lmg4r', 'e0027537', '10.129.35.244', 68, 'aether:1028;pdk:76;skipper:72;schematic:50;netlist:49;pyaether:40;cadence:30;calibre:6;'),
    ('1791790598273_nthdn', 'steveny', '10.129.2.11', 68, 'pyaether:387;aether:174;virtuoso:68;netlist:39;cellview:23;schematic:22;cadence:15;dbget:13;'),
    ('1793002578810_yoman', 'yohannw', '10.129.2.12', 68, 'pyaether:87;cellview:79;aether:71;schematic:40;lib.defs:10;virtuoso:3;dbget:3;cadence:3;'),
    ('1792063718906_u8kbk', 'devonma', '10.129.32.84', 66, 'pdk:182;netlist:44;.gds:40;aether:6;.cdl:6;pyaether:4;calibre:3;.spi:2;'),
    ('1791795200862_zm1g8', 'lizwen', '10.129.2.11', 65, 'aether:357;virtuoso:34;schematic:25;pyaether:15;mixed-signal:12;floorplan:10;lib.defs:6;techfile:4;'),
    ('1791796751454_jtjrm', 'lizwen', '10.129.2.11', 65, 'aether:357;virtuoso:34;schematic:25;pyaether:15;mixed-signal:12;floorplan:10;lib.defs:6;techfile:4;'),
    ('1791796755681_dt95j', 'lizwen', '10.129.2.11', 65, 'aether:357;virtuoso:34;schematic:25;pyaether:15;mixed-signal:12;floorplan:10;lib.defs:6;techfile:4;'),
    ('1791796777274_h1v18', 'lizwen', '10.129.2.11', 65, 'aether:357;virtuoso:34;schematic:25;pyaether:15;mixed-signal:12;floorplan:10;lib.defs:6;techfile:4;'),
    ('1789973566279_0cjq2', 'davidwu', '10.129.40.209', 61, 'aether:477;schematic:241;pyaether:156;floorplan:136;netlist:95;pdk:63;dbopencv:40;cellview:16;'),
    ('1790046970076_ym81m', 'lizwen', '10.129.2.11', 60, 'pyaether:175;calibre:171;aether:143;dbopencv:54;cellview:40;schematic:34;netlist:34;techfile:25;'),
    ('1789955434443_clv6k', 't0002470', '10.129.2.13', 59, 'analog:275;netlist:4;pyaether:3;aether:3;'),
    ('1791782422113_e1ll7', 'steveny', '10.129.2.11', 58, 'cellview:233;schematic:109;pyaether:92;virtuoso:55;dbget:11;netlist:8;aether:7;cadence:3;'),
    ('1790489156584_1bc9r', 'mike', '10.129.32.80', 57, 'analog:294;synopsys:48;pyaether:5;aether:4;pdk:1;'),
    ('1790219126172_4qpyk', 'yanxvwei', '10.129.32.85', 57, 'netlist:80;waveview:34;synopsys:9;'),
    ('1792572273726_qhcja', 'charlesd', '10.129.35.69', 57, 'aether:315;pyaether:46;waveview:19;schematic:16;mixed-signal:13;floorplan:11;netlist:6;virtuoso:3;'),
    ('1790583848095_60xn0', 'ellawu', '10.129.2.14', 57, 'cadence:954;calibre:292;aether:150;.gds:95;cellview:65;schematic:38;virtuoso:13;pyaether:8;'),
    ('1790928288602_o6pnp', 'e0014566', '10.129.2.10', 57, 'virtuoso:282;cellview:35;calibre:29;.gds:26;netlist:25;dbopencellviewbytype:22;ddgetobj:20;cadence:12;'),
    ('1790137149475_ku6wp', 'kevin3d', '10.129.35.69', 56, 'netlist:237;schematic:68;hspice:51;cmos:34;analog:9;transistor:7;aether:5;.gds:3;'),
    ('1789634625396_ew6gi', 'rongjiez', '10.129.2.11', 53, 'dbopencv:150;pyaether:127;schematic:110;cellview:81;dbget:29;aether:14;dbopencellviewbytype:13;virtuoso:5;'),
    ('1782800756855_5u4s2', 'e0025730', '10.129.8.86', 52, 'netlist:182;schematic:55;virtuoso:45;pyaether:8;hspice:7;analog:6;lib.defs:1;aether:1;'),
    ('1792040490093_hi28t', 'alanji', '10.129.35.244', 52, 'cadence:216;aether:172;netlist:146;analog:31;pyaether:13;cellview:12;techfile:6;synopsys:3;'),
    ('1791798218918_krjo2', 'lizwen', '10.129.2.11', 45, 'aether:176;schematic:52;mixed-signal:15;pyaether:11;floorplan:10;lib.defs:7;techfile:4;waveview:1;'),
]
    ("1792378803577_hpy3y", "ruisongs", "10.129.33.207", 82, "netlist:262"),
    ("1792131163281_6sxh5", "e0045488", "10.129.2.11", 82, ".spi:110"),
    ("1788946694927_w5knw", "sagequan", "10.129.32.190", 83, "analog:298"),
    ("1789961307805_2uipn", "ziyuny", "10.129.32.190", 83, "pyaether:169"),
    ("1791947113001_be1i0", "jie23z", "10.129.2.11", 84, "cellview:200"),
    ("1792735101347_oe94r", "jiebings", "10.129.2.10", 84, "aether:167"),
    ("1790230482027_7lp3l", "jiangbaol", "10.129.2.11", 86, "cellview:101"),
]

def sh(ip, cmd, t=60):
    try:
        out = subprocess.run(["ssh","-o","BatchMode=yes","-o","ConnectTimeout=6",ip,cmd],
            capture_output=True, text=True, timeout=t, stdin=subprocess.DEVNULL)
        return out.stdout, out.returncode
    except Exception:
        return "", 998

def extract_user_turns(raw):
    data = None
    try:
        data = json.loads(raw)
    except Exception:
        return []
    msgs = data.get("messages") if isinstance(data, dict) else data
    if not isinstance(msgs, list):
        return []
    turns = []
    for m in msgs:
        if m.get("role") != "user":
            continue
        content = m.get("content"); texts = []
        if isinstance(content, list):
            for c in content:
                if isinstance(c, dict) and c.get("type") == "text":
                    texts.append(c.get("text", ""))
        elif isinstance(content, str):
            texts.append(content)
        for txt in texts:
            if txt.startswith("<user_input"):
                mm = re.search(r'<user_input mode="act">(.+?)</user_input>', txt, re.S)
                if mm: txt = mm.group(1)
            if txt.startswith("<skill_instructions>") or txt.startswith("<environment_details>") or txt.startswith("<attempt_completion"):
                continue
            s = txt.strip()
            if s and not s.startswith("<"):
                turns.append(s)
    return turns

def assistant_signal(raw):
    """Count editor tool uses + extract produced file names from assistant messages."""
    data = None
    try:
        data = json.loads(raw)
    except Exception:
        return 0, []
    msgs = data.get("messages") if isinstance(data, dict) else data
    if not isinstance(msgs, list):
        return 0, []
    nedit = 0
    produced = set()
    for m in msgs:
        if m.get("role") != "assistant":
            continue
        content = m.get("content")
        if isinstance(content, list):
            for c in content:
                if not isinstance(c, dict):
                    continue
                # tool_use blocks
                if c.get("type") == "tool_use":
                    name = c.get("name","")
                    inp = c.get("input", {})
                    if name in ("write_to_file","create_file","editor","apply_diff","insert_content","search_and_replace"):
                        nedit += 1
                        fp = inp.get("path") or inp.get("file") or inp.get("filePath") or ""
                        if fp:
                            produced.add(fp)
                    elif name in ("execute_command","run_command","run_commands","bash"):
                        cmd = inp.get("command","") or inp.get("cmd","")
                        # produce via shell redirect / here-doc
                        for mm in re.finditer(r'>\s*([^\s|;&]+/\S+|[\w./-]+\.\w+)', cmd):
                            produced.add(mm.group(1))
                        for mm in re.finditer(r'\b(?:cat|tee|cp|mv)\s+(?:>?>?\s*)?([\w./-]+\.\w+)', cmd):
                            produced.add(mm.group(1))
                # some formats store text blocks with tool mentions
                elif c.get("type") == "text":
                    txt = c.get("text","")
                    for mm in re.finditer(r'(?:write_to_file|create_file|editor).*?path[":=\s]+([^\s",}]+)', txt):
                        produced.add(mm.group(1))
    return nedit, sorted(produced)

def peek_one(t):
    sid, user, ip, mc, hint = t
    ls = "ls /home/%s/.cline/data/sessions/%s/%s.messages.json 2>/dev/null" % (user, sid, sid)
    out, rc = sh(ip, ls, 20)
    files = [f for f in out.split() if f]
    if not files:
        return (sid, user, ip, mc, ["NO_FILE"], "?", 0, [])
    fpath = files[0]
    sz, _ = sh(ip, "stat -c %%s %s" % fpath, 20)
    # cap cat to avoid huge files: read first 2MB
    out2, _ = sh(ip, "head -c 2000000 %s" % fpath, 90)
    turns = extract_user_turns(out2)
    if not turns:
        for mm in re.finditer(r'<user_input mode="act">(.+?)</user_input>', out2, re.S):
            s = mm.group(1).strip()
            if s and not s.startswith("<"):
                turns.append(s)
    nedit, produced = assistant_signal(out2)
    return (sid, user, ip, mc, turns, sz.strip(), nedit, produced)

if __name__ == "__main__":
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as ex:
        futs = {ex.submit(peek_one, t): t for t in TARGETS}
        for fu in concurrent.futures.as_completed(futs):
            try:
                sid, user, ip, mc, turns, sz, nedit, produced = fu.result()
            except Exception as e:
                t = futs[fu]; sid, user, ip, mc, turns, sz, nedit, produced = t[0], t[1], t[2], t[3], ["EXC:"+str(e)], "?", 0, []
            print("### %s | %s@%s | mc=%s | size=%s | nturns=%d | nedit=%d | produced=%s" % (sid, user, ip, mc, sz, len(turns), nedit, produced))
            for i, tn in enumerate(turns[:6]):
                print("  [U#%d] %s" % (i, tn[:400].replace("\n", " ")))
            print("---")
