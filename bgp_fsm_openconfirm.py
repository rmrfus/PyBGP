#!/usr/bin/env python3

############################################################################
#                                                                          #
#  PyBGP - Python BGP implementation                                       #
#  Copyright (C) 2020  Sebastian Majewski                                  #
#                                                                          #
#  This program is free software: you can redistribute it and/or modify    #
#  it under the terms of the GNU General Public License as published by    #
#  the Free Software Foundation, either version 3 of the License, or       #
#  (at your option) any later version.                                     #
#                                                                          #
#  This program is distributed in the hope that it will be useful,         #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of          #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           #
#  GNU General Public License for more details.                            #
#                                                                          #
#  You should have received a copy of the GNU General Public License       #
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.  #
#                                                                          #
#  Author's email: ccie18643@gmail.com                                     #
#  Github repository: https://github.com/ccie18643/PyBGP                   #
#                                                                          #
############################################################################


import bgp_message


async def fsm_openconfirm(self, event):
    """ Finite State Machine - OpenConfirm state """

    if event.name == "Event 2: ManualStop":
        self.logger.info(event.name)

        # Send the NOTIFICATION with a Cease
        await self.send_notification_message(bgp_message.CEASE)

        # Set ConnectRetryCounter to zero
        self.connect_retry_counter = 0

        # Change state to Idle
        self.change_state("Idle")

    if event.name == "Event 8: AutomaticStop":
        self.logger.info(event.name)

        # Send the NOTIFICATION with a Cease
        await self.send_notification_message(bgp_message.CEASE)

        # Increment the ConnectRetryCounter by 1
        self.connect_retry_counter += 1

        # Change state to Idle
        self.change_state("Idle")

    if event.name == "Event 10: HoldTimer_Expires":
        self.logger.info(event.name)

        # Send a NOTIFICATION message with the error code Hold Timer Expired
        await self.send_notification_message(bgp_message.HOLD_TIMER_EXPIRED)

        # Increment ConnectRetryCounter
        self.connect_retry_counter += 1

        # Change state to Idle
        self.change_state("Idle")

    if event.name == "Event 11: KeepaliveTimer_Expires":
        self.logger.info(event.name)

        # Send KEEPALIVE message
        await self.send_keepalive_message()

        # Restart the KeepaliveTimer
        self.keepalive_timer = self.keepalive_time

    if event.name in {"Event 18: TcpConnectionFails", "Event 25: NotifMsg"}:
        self.logger.info(event.name)

        # Increment the ConnectRetryCounter by 1
        self.connect_retry_counter += 1

        # Change state to Idle
        self.change_state("Idle")

    if event.name in {"Event 21: BGPHeaderErr", "Event 22: BGPOpenMsgErr"}:
        self.logger.info(event.name)

        message = event.message

        # Send a NOTIFICATION message with the appropriate error code
        await self.send_notification_message(message.message_error_code, message.message_error_subcode, message.message_error_data)

        # Increment ConnectRetryCounter
        self.connect_retry_counter += 1

        # Change state to Idle
        self.change_state("Idle")

    if event.name == "Event 24: NotifMsgVerErr":
        self.logger.info(event.name)

        # Change state to Idle
        self.change_state("Idle")

    if event.name == "Event 26: KeepAliveMsg":
        self.logger.info(event.name)

        # Restart the HoldTimer
        self.hold_timer = self.hold_time

        # Change state to Established
        self.change_state("Established")

    if event.name in {
        "Event 9: ConnectRetryTimer_Expires",
        "Event 12: DelayOpenTimer_Expires",
        "Event 13: IdleHoldTimer_Expires",
        "Event 20: BGPOpen with DelayOpenTimer running",
        "Event 27: UpdateMsg",
        "Event 28: UpdateMsgErr",
    }:
        self.logger.info(event.name)

        # Send the NOTIFICATION with the Error Code Finite State Machine Error
        await self.send_notification_message(bgp_message.FINITE_STATE_MACHINE_ERROR)

        # Increment the ConnectRetryCounter by 1
        self.connect_retry_counter += 1

        # Chhange state to Idle
        self.switch_state("Idle")
