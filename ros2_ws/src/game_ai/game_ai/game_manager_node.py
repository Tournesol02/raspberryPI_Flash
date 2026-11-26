#!/usr/bin/env python3
"""Game session manager."""

""""Terminal 1 - initialize game"""
""""ros2 run game_ai game_manager_node"""

""""Terminal 2 - observe sequence"""
""""ros2 topic echo /game/sequence"""

""""Terminal 3 - play game"""
#Start and restart
""""ros2 service call /game/start std_srvs/srv/Trigger "{}" """
#Send sequence
""""ros2 topic pub --once /game/player_input std_msgs/msg/Int32MultiArray "{data: [2]}" """
""""ros2 topic pub --once /game/player_input std_msgs/msg/Int32MultiArray "{data: [2, 4]}" """
"""" ... """
#Send move to perform to autonomous node
""""ros2 topic pub --once /autonomous_command  interfaces/msg/AutonomousCommand "{movetype: 1, movement_done: false}" """
import random

import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool, Int32MultiArray
from std_srvs.srv import Trigger
from interfaces.msg import AutonomousCommand



class GameManagerNode(Node):
    MAX_STEPS = 3

    def __init__(self):
        super().__init__('game_manager_node')

        self.sequence = []
        self.game_running = False
        self.autonomous_ack  = False

        # Publish current sequence: [1], [1, 4], [1, 4, 2], ...
        self.sequence_publisher = self.create_publisher(
            Int32MultiArray, '/game/sequence', 10
        )

        # Evaluate player answer.
        self.result_publisher = self.create_publisher(
            Bool, '/game/correct', 10
        )

        # Receive player list
        self.player_subscription = self.create_subscription(
            Int32MultiArray,
            '/game/player_input',
            self.verify_player_sequence,
            10,
        )

        # Starts or restart game.
        self.start_service = self.create_service(
            Trigger, '/game/start', self.start_game
        )

        self.command_publisher = self.create_publisher(
            AutonomousCommand,
            '/autonomous_command',
            10
        )

        self.ack_autonomous = self.create_subscription(
            AutonomousCommand,
            '/movement_ack',
            self.recv_autonomous_ack,
            10
        )

        self.ready_publisher = self.create_publisher(
            Bool,
            '/game/ready_for_input',
            10
        )

        self.get_logger().info('Game manager ready. Call /game/start.')

    def start_game(self, request, response):
        self.sequence = []
        self.game_running = True

        response.success = True
        response.message = 'Game started. First sequence published.'
        return response

    # get autonomous node ack

    def recv_autonomous_ack(self, message):
        self.autonomous_ack = message.movement_done
        self.get_logger().info('Ack received from autonomous')


    # check if player performed sequence is same

    def verify_player_sequence(self, message):
        """Generate next movement after review"""
        if not self.game_running:
            self.get_logger().warn('No active game. Call /game/start first.')
            return

        player_input = list(message.data)
        correct = player_input == self.sequence
        self.result_publisher.publish(Bool(data=correct))

        if not correct:
            self.get_logger().warn(
                f'Incorrect sequence: {player_input}. '
                f'Expected {len(self.sequence)} moves. Try again.'
            )
            return  # For now - after will restart the game.

        self.get_logger().info('Correct sequence!')

        if len(self.sequence) >= self.MAX_STEPS:
            self.game_running = False
            self.get_logger().info('Game finished: 20 rounds completed!')
            return

        self.add_move()  # only after right answer.

    # publish towards Screen node if step was correctly done or not

    def publish_step_correctness(self, correct):

        message = Bool(data=correct)
        self.ready_publisher.publish(message)


    # callback that store in Node attribute the AI detected movement and, later, in another function, compare to expected movement.
    # create self.ai_move_detected : direction

    def get_performed_move(self, message):        

        pass

    # should be call when game launch topic sent from Movement detect Node is set to true
    # generate the sequence to perform
    # send one by one to autonomous node and screen node
    # wait for acknowledgment
    # once all the step is performed by the car and displayed by the screen, publishes the detected movement from AI
    # compare expected step with detected one and publish one the screen whether the player has correctly performed the step or not
    # reapeat all of the above until the last sequence is done 

    def run_game(self):

        seq_move_number = 1
        self.add_move_to_seq()

        while len(self.sequence) <= self.MAX_STEPS:

            for move in self.sequence:

                self.publish_move_to_perform(move)
                self.wait_for_ack()
                self.ack_autonomous = False

    

    # publish on the movement_to_perform topic the move to perform, would be received by Auto and Screen Node
    # move : move to publish

    def publish_move_to_perform(self, move):

        command = AutonomousCommand()
        command.movetype = move
        command.movement_done = False
        self.command_publisher.publish(command)

    # return a new step to append in self.sequence

    def get_step(self):

        return random.randint(1,4)

    # add move to the whole sequence

    def add_move_to_seq(self):

        move = self.get_step()
        self.sequence.append(move)

        # developper help

        message = Int32MultiArray()
        message.data = self.sequence.copy()
        self.sequence_publisher.publish(message)

        self.get_logger().info(
            f'Round {len(self.sequence)} - sequence: {self.sequence}'
        )

    
    # clear sequence moves for a new sequence to generate

    def clear_sequence(self):

        self.sequence = []


    # wait for run

    def wait_for_run(self):

        self.get_logger().info('WAITING FOR RUN')

        # read game_running value, true or false

        while(not self.game_running):

            time.sleep(1)

        # launch game 

        self.get_logger().info('RUNNING GAME MANAGER')

        self.run_game()

    
    # wait for ack

    def wait_for_ack(self):

        self.get_logger().info('WAITING FOR ACK')

        # read game_running value, true or false

        while(not self.ack_autonomous):

            time.sleep(0.2)
        
        self.get_logger().info('RECEIVED ACK')


def main(args=None):
    rclpy.init(args=args)
    node = GameManagerNode()
    node.get_logger().info('Game manager ready. Waiting for run or Send topic /game/start.')
    node.wait_for_run()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
