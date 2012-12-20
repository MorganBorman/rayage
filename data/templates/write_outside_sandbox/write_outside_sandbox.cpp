#include <stdio.h>

int main() {
    FILE *fp = fopen("/tmp/test.txt", "w");
    
    fprintf(fp, "Testing...\n");
    
    fclose(fp);
    
    return 0;
}
