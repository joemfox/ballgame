import { useEffect, useState } from 'react'

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import axios from 'axios'

import { ScrollArea } from "@/components/ui/scroll-area"


import StatlineTable from '@/components/StatlineTable.jsx'

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
        <ScrollArea className="h-full">
        <Tabs defaultValue="hitters" className="">
          <TabsList>
            <TabsTrigger value="hitters">Hitters</TabsTrigger>
            <TabsTrigger value="pitchers">Pitchers</TabsTrigger>
          </TabsList>
          <TabsContent value="hitters">
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
         </TabsContent>
         <TabsContent value="pitchers">
        <StatlineTable
          columns={statlineColumns} 
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
         </TabsContent>
         </Tabs>
        </ScrollArea>

  )
}
