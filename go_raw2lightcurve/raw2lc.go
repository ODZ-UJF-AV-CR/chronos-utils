package main

import (
   //"io"
   "os"
   "fmt"
   "encoding/csv"
   "strconv"
)

func main() {
   //filename := "/home/roman/Dokumenty/2022-09-09-11-46-21.223026-lightning.raw"
   filename := os.Args[1]
   file, _ := os.Open(filename)
   csvFile, _ := os.Create(filename[:len(filename)-4]+".csv")
   csvwriter := csv.NewWriter(csvFile)

   fmt.Println("Nacten soubor")

   width := 928
   height := 928
   frame := 0

      for {
          frame++
          if (frame % 25) == 0 {
              fmt.Println("Frame:", frame)
          }
          value := 0
          data := make([]byte, 3*width*height)
          count, _ := file.Read(data)

          if count < width*height*3 {
            break;
          }

          for i:=0; i<width*height; i++ {
              value += int(data[0+i*3] << 4) + int((data[1+i*3] & 0xf0) << 8)
              value += int(data[2+i*3] << 8) + int((data[1+i*3] & 0x0f) << 4)
             // value += (data[0] << 4 | data[1]) + (data[1] | data[2])
          }

          //fmt.Println("Suma", value, count)
          row := []string{strconv.Itoa(frame), strconv.Itoa(value)}
          _ = csvwriter.Write(row)
      }

    csvwriter.Flush()
    csvFile.Close()

}
