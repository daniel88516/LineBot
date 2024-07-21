#include <string>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <queue>
using namespace std;
struct TreeNode
{
    int val;
    TreeNode *left;
    TreeNode *right;
    TreeNode() : val(0), left(nullptr), right(nullptr) {}
    TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
    TreeNode(int x, TreeNode *left, TreeNode *right) : val(x), left(left), right(right) {}
};;
class Solution
{
public:
    /*
    description : {parent, child, isLeft}
    請依此建立一個BinaryTree
     */
    TreeNode *createBinaryTree(vector<vector<int>> &descriptions)
    {
        unordered_map<int, TreeNode *> nodeMap;
        unordered_set<int> childSet;
        for (auto &d : descriptions)
        {
            // parent, child, isLeft
            int parent = d[0], child = d[1], isLeft = d[2];
            // 沒有找到, 建立新的 Node
            if (nodeMap.find(parent) == nodeMap.end())
            {
                nodeMap.insert({parent, new TreeNode(parent)});
            }
            if (nodeMap.find(child) == nodeMap.end())
            {
                nodeMap.insert({child, new TreeNode(child)});
            }
            // 令 parent 指向 node
            if (isLeft)
            {
                nodeMap[parent]->left = nodeMap[child];
            }
            else
            {
                nodeMap[parent]->right = nodeMap[child];
            }
            childSet.insert(child);
        }
        // find root
        for (const auto &pair : nodeMap)
        {
            if (childSet.find(pair.first) == childSet.end())
            {
                return pair.second;
            }
        }
        return nullptr;
    }
};