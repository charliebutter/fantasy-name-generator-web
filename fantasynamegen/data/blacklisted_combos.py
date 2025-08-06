"""
Blacklisted character combinations organized by severity level.

This file contains patterns that should be avoided in fantasy name generation,
organized by severity levels 1-5, where 1 is the most severe and should be
avoided most aggressively.
"""

# BLACKLISTED_COMBOS_BY_LEVEL - Remains the same as Tuned v5
BLACKLISTED_COMBOS_BY_LEVEL = {
    # Level 5: Common difficult clusters
    5: ["thl", "thr", "sht", "shn", "skr", "spl", "spr", "str", "chth", "phth", "oue",
        # Added more common difficult clusters
        "tsk", "tsx", "tsl", "tsm", "tsn", "tsp", "tsr", "tsw", "tsy", "tsz",
        "scl", "scr", "scw", "shm", "shn", "shp", "shr", "sht", "shw", "shy",
        "sfl", "sfr", "sgr", "skl", "skw", "sky", "slm", "sln", "slp", "slw",
        "smr", "snl", "snr", "snw", "spw", "spy", "srw", "sry", "stl", "stw",
        "swl", "swr", "swy", "szl", "szr", "szw", "szy"],
        
    # Level 4: Harsh combinations
    4: ["bk", "bp", "bd", "db", "dp", "dk", "gb", "gp", "gd", "kb", "kp", "kd", "pb", "pk", "pd", "tb", "tp",
        "sb", "sd", "sg", "sv", "szk", "szp", "szt", "szd", "sq",
        "rbg", "rdz", "rks", "rxk", "rxg", "rxd", "rxb", "rpz", "rtz",
        "aoo", "eoo", "ioo", "ouu", "yuu", "aeu", "eiu", "iou", "oau", "uai",
        "aio", "eao", "iao", "oai", "uei", "aoi", "eei", "iui", "oeo", "uau", "iiu", "uuo", "uui",
        "jq", "qj", "qx", "xq", "jx", "xj", "vq", "qv", "wq", "qw", "zq", "qz",
        "cq", "qc", "gq", "qg", "kq", "qk", "pq", "qp", "tq", "qt",
        "bz", "dz", "gz", "vz",
        "ao", "eo", "iu", "oa", "oe", "ua", "ue", "ui", "uo", "uy", "yi", "iy",
        "bg", "bm", "bp", "bq", "bv", "bw", "bx", "by", "bz",
        "cb", "cd", "cf", "cg", "ck", "cm", "cp", "cq", "cv", "cw", "cx", "cy", "cz",
        "db", "dc", "df", "dg", "dk", "dm", "dq", "dv", "dw", "dx", "dy",
        "fb", "fc", "fd", "fg", "fk", "fm", "fp", "fq", "fv", "fw", "fx", "fy", "fz",
        "gc", "gf", "gk", "gm", "gq", "gv", "gw", "gx", "gy",
        "hb", "hc", "hd", "hf", "hg", "hj", "hk", "hm", "hp", "hq", "hv", "hw", "hx", "hy", "hz",
        "jb", "jc", "jd", "jf", "jg", "jh", "jk", "jm", "jp", "jr", "jt", "jv", "jw", "jy", "jz",
        "kb", "kc", "kf", "kg", "kj", "km", "kq", "kv", "kw", "kx", "ky", "kz",
        "lb", "lc", "ld", "lf", "lg", "lj", "lk", "lm", "lq", "lv", "lw", "lx", "ly", "lz",
        "mb", "mc", "md", "mf", "mg", "mh", "mk", "mq", "mv", "mw", "mx", "my", "mz",
        "nb", "nc", "nd", "nf", "ng", "nh", "nk", "nm", "nq", "nv", "nw", "nx", "ny", "nz",
        "pb", "pc", "pd", "pf", "pg", "pk", "pm", "pn", "pq", "pv", "pw", "px", "py", "pz",
        "rb", "rc", "rd", "rf", "rg", "rh", "rj", "rk", "rm", "rq", "rv", "rw", "rx", "ry", "rz",
        "sb", "sc", "sf", "sg", "sh", "sj", "sk", "sm", "sq", "sv", "sw", "sx", "sy", "sz",
        "tb", "tc", "td", "tf", "tg", "tj", "tk", "tm", "tq", "tv", "tw", "tx", "ty", "tz",
        "vb", "vc", "vd", "vf", "vg", "vh", "vj", "vk", "vm", "vn", "vp", "vr", "vs", "vt", "vw", "vx", "vy",
        "wb", "wc", "wd", "wf", "wg", "wh", "wj", "wk", "wm", "wn", "wp", "wr", "ws", "wt", "wv", "wz",
        "xb", "xc", "xd", "xf", "xh", "xi", "xk", "xm", "xn", "xo", "xp", "xr", "xs", "xt", "xu", "xv", "xy"],
        
    # Level 3: Difficult combinations
    3: ["kh", "gh", "bh", "dh", "nj", "mj", "bj", "gj", "dj", "sf", "ft", "kt", "pt",
        "bn", "cn", "fn", "gm", "mn", "pf",
        "qf", "qm", "qn", "qv", "qw", "qy", "wx", "wy",
        "nzr", "nzl", "nzt", "nzd", "nzg", "mzr", "mzl", "ndg", "nkg", "nbg", "nkd", "ngz",
        "nkb", "nkp", "nkt", "npk", "npg", "ndb", "ndp", "ndt", "ntd", "ntb", "ntp", "mgd", "mgz",
        "mkb", "mkp", "mkt", "mtk", "mpk", "mpg", "mbd", "mbg", "mdb", "mdg", "mgb", "mgd",
        "aie", "eie", "oie", "uie", "aiu", "oiu", "iua", "uio", "ioi", "ooi",
        # Added more aspirated and nasal combinations
        "ch", "fh", "jh", "lh", "mh", "nh", "ph", "rh", "sh", "th", "vh", "wh", "yh", "zh",
        "hm", "hn", "hp", "hr", "hs", "ht", "hv", "hw", "hy", "hz",
        "nl", "nm", "np", "nr", "ns", "nt", "nv", "nw", "ny",
        "ml", "mp", "mr", "ms", "mt", "mv", "mw", "my",
        "lg", "lh", "lj", "lk", "lq", "lv", "lw", "lx", "ly", "lz",
        "rg", "rh", "rj", "rk", "rq", "rv", "rw", "rx", "ry", "rz",
        # More vowel sequences
        "aae", "aai", "aao", "aau", "aay", "aea", "aei", "aeo", "aeu", "aey",
        "aia", "aie", "aio", "aiu", "aiy", "aoa", "aoe", "aoi", "aou", "aoy",
        "aua", "aue", "aui", "auo", "auy", "aya", "aye", "ayi", "ayo", "ayu",
        "eae", "eai", "eao", "eau", "eay", "eea", "eei", "eeo", "eeu", "eey",
        "eia", "eie", "eio", "eiu", "eiy", "eoa", "eoe", "eoi", "eou", "eoy",
        "eua", "eue", "eui", "euo", "euy", "eya", "eye", "eyi", "eyo", "eyu"],
        
    # Level 2: Very problematic
    2: ["qk", "qp", "qz", "jx", "jq", "jz", "vz", "vx", "vq", "wx", "wq", "wz",
        "bv", "cj", "dg", "fv", "gj", "kg", "td", "dt", "bt", "gt",
        "bsk", "bsp", "bst", "dsk", "dsp", "dst", "gsk", "gsp", "gst",
        "rcb", "rcd", "rcg", "rdg", "rfg", "rkg", "rpg", "rtg", "rjb", "rjd", "rjg", "rjk",
        "rvb", "rvd", "rvg", "rvk", "rvp", "rvt",
        "ssx", "ssz", "szs", "szx", "xss", "xsz", "zss", "zsx", "zsz", "xzs", "xzz", "zxs",
        "zxz", "scz", "szc", "zcs", "zcz", "tzs", "tsz", "zts", "ztz",
        # Added more sibilant combinations and harsh clusters
        "ssj", "ssl", "ssm", "ssn", "ssp", "ssr", "sst", "ssv", "ssw", "ssy",
        "zzb", "zzc", "zzd", "zzf", "zzg", "zzh", "zzj", "zzk", "zzl", "zzm",
        "zzn", "zzp", "zzq", "zzr", "zzt", "zzv", "zzw", "zzy",
        "xxb", "xxc", "xxd", "xxf", "xxg", "xxh", "xxj", "xxk", "xxl", "xxm",
        "xxn", "xxp", "xxq", "xxr", "xxs", "xxt", "xxv", "xxw", "xxy", "xxz",
        "qqb", "qqc", "qqd", "qqf", "qqg", "qqh", "qqj", "qqk", "qql", "qqm",
        "qqn", "qqp", "qqr", "qqs", "qqt", "qqv", "qqw", "qqx", "qqy", "qqz",
        # Triple consonant clusters
        "bcd", "bcf", "bcg", "bch", "bcj", "bck", "bcl", "bcm", "bcn", "bcp",
        "bcr", "bcs", "bct", "bcv", "bcw", "bcx", "bcy", "bcz",
        "cdf", "cdg", "cdh", "cdj", "cdk", "cdl", "cdm", "cdn", "cdp",
        "cdr", "cds", "cdt", "cdv", "cdw", "cdx", "cdy", "cdz",
        "dfg", "dfh", "dfj", "dfk", "dfl", "dfm", "dfn", "dfp",
        "dfr", "dfs", "dft", "dfv", "dfw", "dfx", "dfy", "dfz",
        # More problematic vowel combinations
        "yaa", "yae", "yai", "yao", "yau", "yea", "yee", "yei", "yeo", "yeu",
        "yia", "yie", "yii", "yio", "yiu", "yoa", "yoe", "yoi", "yoo", "you",
        "yua", "yue", "yui", "yuo", "yuu"],
        
    # Level 1: Most severe
    1: ["qxz", "jqx", "vzx", "wzx", "zxq", "xqz", "xzq", "zqx", "qzx", "bcdn", "ghjk",
        "bscr", "bzdr", "ckstr", "dscr", "dspr", "dzdr", "fthm", "gscr", "gspr", "gzdr",
        "kstr", "kspr", "kzdr", "lsthr", "mscr", "mspr", "mzdr", "nscr", "nspr", "nzdr",
        "pscr", "pspr", "pzdr", "rscr", "rspr", "rzdr", "sfth", "sfthr", "sktr", "skstr",
        "tscr", "tspr", "tzdr", "vscr", "vspr", "vzdr", "xscr", "xspr", "xzdr", "zscr", "zspr", "zzdr",
        "rgrv", "zrz", "zssx", "tkt", "pkt", "dkt", "gkt", "bkt", "fkt",
        "zbl", "zdl", "zgl", "zkl", "zpl", "zrp", "zrt", "zrv", "zrx", "zrz", "ztl",
        "zml", "znl", "zkw", "zpw", "ztw", "zjr", "zjl", "zhw",
        "xbl", "xcl", "xdl", "xfl", "xgl", "xkl", "xpl", "xsl", "xtl", "xvl", "xzl",
        "xg", "xj", "xq", "xw", "xx", "xz",
        "qxzw", "jqxz", "vzxq", "wzxq", "zxqw", "xqzw", "xzqw", "zqxw", "qzxw",
        "qxzj", "jqxw", "vzxj", "wzxj", "zxqj", "xqzj", "xzqj", "zqxj", "qzxj",
        "qxzy", "jqxy", "vzxy", "wzxy", "zxqy", "xqzy", "xzqy", "zqxy", "qzxy",
        "xzqw", "zxqy", "qxzv", "xqzv", "zqxv", "vqxz", "vxqz", "vzqx",
        "aaa", "eee", "iii", "ooo", "uuu", "aae", "aai", "aao", "aau", "aea", "aei", "aeo", "aeu",
        "aia", "aie", "aio", "aiu", "aoa", "aoe", "aoi", "aou", "aua", "aue", "aui", "auo",
        "eaa", "eae", "eai", "eao", "eau", "eea", "eei", "eeo", "eeu", "eia", "eie", "eio", "eiu",
        "eoa", "eoe", "eoi", "eou", "eua", "eue", "eui", "euo", "iaa", "iae", "iai", "iao", "iau",
        "iea", "iee", "ieo", "ieu", "iia", "iie", "iio", "iiu", "ioa", "ioe", "ioi", "iou",
        "iua", "iue", "iui", "iuo", "oaa", "oae", "oai", "oao", "oau", "oea", "oee", "oei", "oeo",
        "oeu", "oia", "oie", "oii", "oio", "oiu", "ooa", "ooe", "ooi", "oou", "oua", "oue", "oui", "ouo",
        "uaa", "uae", "uai", "uao", "uau", "uea", "uee", "uei", "ueo", "ueu", "uia", "uie", "uii",
        "uio", "uiu", "uoa", "uoe", "uoi", "uoo", "uou", "uua", "uue", "uui", "uuo",
        # Four+ letter vowel clusters
        "aaae", "aaai", "aaao", "aaau", "aaay", "aeee", "aeei", "aeeo", "aeeu", "aeey",
        "aiii", "aiie", "aiio", "aiiu", "aiiy", "aooo", "aooe", "aooi", "aoou", "aooy",
        "auuu", "auue", "auui", "auuo", "auoy", "ayee", "ayei", "ayeo", "ayeu", "ayey",
        "eaaa", "eaae", "eaai", "eaao", "eaau", "eeea", "eeei", "eeeo", "eeeu", "eeey",
        "eiaa", "eiae", "eiai", "eiao", "eiau", "eoaa", "eoae", "eoai", "eoao", "eoau",
        "euaa", "euae", "euai", "euao", "euau", "eyaa", "eyae", "eyai", "eyao", "eyau"]
}