import { useEffect, useState } from 'react'
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable"
import axios from 'axios'

import { ScrollArea } from "@/components/ui/scroll-area"
import { DndProvider } from 'react-dnd'
import { HTML5Backend } from 'react-dnd-html5-backend'

import StatlineTable from '@/components/StatlineTable.jsx'
import LineupCard from '@/components/Lineup.jsx'
import {statlineColumns, FAN_columns} from '../lib/dataColumns'

export default function Team() {
  const [players, setPlayers] = useState([])
  const [{ pageIndex, pageSize }, setPagination] = useState({ pageIndex: 0, pageSize: 100 })
  const [pageCount, setPageCount] = useState(-1)

  const defaultSort = {desc:true,id:'FAN_total'}
  const [sorting, setSorting] = useState([defaultSort])

  const [metrics,setMetrics] = useState([])
  
  const [filters, setColumnFilters] = useState([])
  const [positionFilters, setPositionFilters] = useState({
      "C": false,
      "1B": false,
      "2B": false,
      "SS": false,
      "3B": false,
      "LF": false,
      "CF": false,
      "RF": false,
      "SP": false,
      "RP": false,
  })

  useEffect(() => {
    let params = new URLSearchParams()
    params.append('page', pageIndex + 1)
    params.append('ordering', sorting.length > 0 ? sorting.map(d => `${d.desc ? '-' : ''}${d.id}`).join(',') : '-FAN_total')
    params.append('search', filters.map(d => d.value).join(''))
    for (let position in positionFilters) {
        if (positionFilters[position]) {
            params.append('positions', position)
        }
    }
    console.log(params)
    axios.get(`http://localhost:8000/api/players/2023`, {
        params: params
    })
        .then(response => {
            if (response.data.results) {
                let count = Math.ceil(response.data.count / response.data.results.length)
                setMetrics({'avg':response.data.avg_total,'stdDev':response.data.stddev_total})
                setPageCount(count)
                setPagination({ pageIndex: pageIndex, pageSize: response.data.results.length })
                setPlayers(response.data.results)
            }
        })
        .catch(err => {
            console.log(err)
        })
}, [pageIndex, sorting, filters,positionFilters])

  return (
    <DndProvider backend={HTML5Backend}>
    <ResizablePanelGroup className="border  max-h-screen" direction="horizontal">
      <ResizablePanel defaultSize={40}>
        <ScrollArea className="relative h-full">
        <LineupCard team={"TST"}/>
        </ScrollArea>
        </ResizablePanel>
      <ResizableHandle withHandle/>
      <ResizablePanel>
        <ScrollArea className="h-full">
        <StatlineTable
          columns={FAN_columns} 
          metrics={metrics}
          data={players}
          setData={setPlayers}
          pageIndex={pageIndex}
          pageSize={pageSize}
          pagination={{ pageIndex: pageIndex, pageSize: pageSize }}
          pageCount={pageCount}
          setPagination={setPagination}
          sorting={sorting}
          setSorting={setSorting}
          filters={filters}
          setColumnFilters={setColumnFilters}
          positionFilters={positionFilters}
          setPositionFilters={setPositionFilters}
         />
        </ScrollArea>
        </ResizablePanel>
    </ResizablePanelGroup>
    </DndProvider>
  )
}
