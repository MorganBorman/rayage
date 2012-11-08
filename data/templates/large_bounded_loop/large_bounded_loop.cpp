#include <iostream>
using namespace std;

int main(int argc, char* argv[])
{
  int i = 0;
  while (i < 1000*1000*100) {
    i++;
  }
  cout << "After the loop the value of i is: " << i << ".\n";
}