package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os"

	"time"

	"github.com/confluentinc/confluent-kafka-go/kafka"
	"github.com/gorilla/websocket"
)

func MockWebsocketHandler(w http.ResponseWriter, r *http.Request, c *kafka.Consumer, sigchan chan os.Signal) {
	upgrader.CheckOrigin = func(r *http.Request) bool { return true }
	conn, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		fmt.Printf("Error while upgrading connection: %s\n", err)
		return
	}
	defer conn.Close()
	// go sendPickInterval(conn)

	for {
		select {
		case sig := <-sigchan:
			fmt.Printf("Caught signal %v: terminating\n", sig)
			return
		default:
			ev := c.Poll(10000)
			if ev == nil {
				fmt.Println("No message received")
				continue
			}

			switch e := ev.(type) {
			case *kafka.Message:
				message := make(map[string]interface{})
				message["topic"] = e.TopicPartition.Topic
				message["value"] = string(e.Value)
				fmt.Println("Got message")
				fmt.Println(message)

				jsonData, err := json.Marshal(message)
				if err != nil {
					fmt.Printf("Error encoding message: %s\n", err)
					continue
				}

				if err := conn.WriteMessage(websocket.TextMessage, jsonData); err != nil {
					fmt.Printf("Error sending Kafka message over WebSocket: %s\n", err)
					return
				}
			case kafka.Error:
				fmt.Printf("Error while consuming: %v\n", e)
			}
		}
	}
}

func sendPickInterval(conn *websocket.Conn) {
	for {
		time.Sleep(60 * time.Second)
		message := make(map[string]interface{})
		data := make(map[string]interface{})

		data["type"] = "p"
		data["station"] = "BKB"
		data["channel"] = "BHE"
		data["arrival"] = time.Now().UTC()
		message["topic"] = "pick"
		message["value"] = data
		fmt.Println("--------------------------------")

		jsonData, err := json.Marshal(message)
		if err != nil {
			fmt.Printf("Error encoding message: %s\n", err)
			continue
		}

		if err := conn.WriteMessage(websocket.TextMessage, jsonData); err != nil {
			fmt.Printf("Error sending Kafka message over WebSocket: %s\n", err)
			return
		}

		time.Sleep(5 * time.Second)

	}
}
