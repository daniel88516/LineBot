#include <iostream>
using namespace std;
template <typename T, typename Pred>
int countMatchElements(T *begin, T *end, Pred pred)
{
    int count = 0;
    for (; begin != end; ++begin)
    {
        if (pred(*begin))
            ++count;
    }
    return count;
}
int main(void)
{
    string stringArray[] = {"something", "", "a", "b", "c", "d"};

    auto isTinyString = [](auto &val) -> bool
    { return val.size() < 3; };
    std::cout << countMatchElements(stringArray, stringArray + 6, isTinyString) << std::endl;
}
