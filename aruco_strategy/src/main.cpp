#include <behavior_tree.h>

#include <button_check.h>
#include <push_plan.h>

int main(int argc, char** argv)
{
  ros::init(argc, argv, "strategy_node");

  try
  {
    int tick_per_in_milliseconds = 1000;
    BT::SequenceNodeWithMemory* root = new BT::SequenceNodeWithMemory("main_sequence");
    BT::ROSCondition* cond   = new BT::ROSCondition("button_checker");
    BT::ROSAction*    uc0 = new BT::ROSAction("uc_action0");
    BT::ROSAction*    uc1 = new BT::ROSAction("uc_action");
    BT::ROSAction*    uc2 = new BT::ROSAction("uc_action1");
    BT::ROSAction*    uc3 = new BT::ROSAction("uc_action2");
    BT::ROSAction*    uc4 = new BT::ROSAction("uc_action3");
    BT::ROSAction*    uc5 = new BT::ROSAction("uc_action4");
    BT::ROSAction*    uc6 = new BT::ROSAction("uc_action5");
    // BT::ROSAction*    mb2 = new BT::ROSAction("mb2_action");

    root->AddChild(cond);
    root->AddChild(uc0);
    root->AddChild(uc1);
    root->AddChild(uc2);
    root->AddChild(uc3);
    root->AddChild(uc4);
    root->AddChild(uc5);
    root->AddChild(uc6);
    // root->AddChild(mb2);

    Execute(root, tick_per_in_milliseconds);

    delete uc1;
    delete uc2;
    delete uc3;
    delete uc4;
    delete uc5;
    delete uc6;
    delete uc0;
    // delete mb2;
    delete cond;
    delete root;
  }
  catch(BT::BehaviorTreeException& e)
  {
    std::cerr << e.what() << '\n';
  }

  return 0;
}