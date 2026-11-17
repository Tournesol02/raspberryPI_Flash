
#include "rclcpp/rclcpp.hpp"

#include <chrono>
#include <functional>
#include <memory>
#include <algorithm>
#include <cstdint>
#include <cstdlib>

#include "interfaces/msg/motors_order.hpp"
#include "interfaces/msg/autonomous.hpp"

using namespace std::chrono_literals;
using std::placeholders::_1;

class game_engine : public rclcpp::Node
{
public:


  void game_engine(int num_loop){
    int random = 0;
    for(int i = 0; i<num_loop;i++){
      random =  rand() % 5;
      switch(random){
      case(0){
	avance(50);
      }
      case(1){
	reculer(50);
      }
      case(2){
	droite(50);
      }
      case(3){
	gauche(50);
      }
      }
    }
    arreter();
  }
      
int main(int argc, char * argv[])
{
    rclcpp::init(argc, argv);

    auto node = std::make_shared<autonomous_drive>();

    rclcpp::spin(node);

    rclcpp::shutdown();

    return 0;
}
