#include <sys/types.h>
#include <unistd.h>
#include <stdio.h>
#include <string.h>

/*
 * mcchown <file>
 *   Change the user and group owenership of the given file or directory to 1000:1000.
 *
 *   For security, the given path will be interpreted as relative to ROOT_DIR below
 *     and limited to a maximum length of MAX_LEN.
 */

const char * ROOT_DIR = "/mnt/minecraft";
const unsigned int MAX_LEN = 64;


void main(int argc, char* argv[]) {
    //set UID to root
    setuid(0);

    //allocate string based on parameter length
    char outstr[strnlen(argv[1],MAX_LEN)+strnlen(ROOT_DIR,MAX_LEN)+1];

    //prepend ROOT_DIR to input path for increased security
    snprintf( outstr, strnlen(argv[1],MAX_LEN)+strnlen(ROOT_DIR,MAX_LEN)+1, "%s%s", ROOT_DIR, argv[1] );
    //printf("%s\n", outstr);

    //change file ownership
    chown( outstr, 1000, 1000 );
}

