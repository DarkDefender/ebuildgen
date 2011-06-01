#ifdef IFDEF1
    #include "ifdef1.h"
#endif

#include    <glob1.h>
#include <io>
#include <glob2.h>
#include "loc1.h"
/*
#include "comment.h"
sdasdasdasd */
// #include "linecom.h"
#include "loc2.h"
#include <strings>
/* ok... */
#include <glob3.h>

#if                 0
 #if 0
             
 #endif
#include <if0_wrong.h>
#endif

#ifdef IFDEF2
    #include <ifdef2.h>
#endif

#include "loc3.h"

#ifdef IFDEF2
    #include <ifdef2.h>
    #ifdef IFDEF3
        #include "ifdef3.h"
    #endif
    #include "ifdef2.h"
#endif

#ifdef IFDEF2
    #ifdef IFDEF3
        #include <ifdef3.h>
    #endif
#endif
