#include <stdio.h>

int main() {
    FILE *fp = fopen("test.txt", "w");
    
    fprintf(fp, "Testing...\n");
    
    fclose(fp);
    
    return 0;
}
