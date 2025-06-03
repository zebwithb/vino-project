/** @jsxImportSource @emotion/react */


import { Fragment } from "react"
import { isTrue } from "$/utils/state"
import Error from "next/error"
import { useClientSideRouting } from "$/utils/client_side_routing"
import NextHead from "next/head"
import { jsx } from "@emotion/react"



export function Fragment_d0bdc6abf12da3a0029322b41e7c0a07 () {
  

  const routeNotFound = useClientSideRouting()




  
  return (
    jsx(
Fragment,
{},
(isTrue(routeNotFound) ? (jsx(
Fragment,
{},
jsx(Error,{statusCode:404},)
,)) : (jsx(
Fragment,
{},
))),)
  )
}

export default function Component() {
    




  return (
    jsx(
Fragment,
{},
jsx(Fragment_d0bdc6abf12da3a0029322b41e7c0a07,{},)
,jsx(
NextHead,
{},
jsx(
"title",
{},
"404 - Not Found"
,),jsx("meta",{content:"The page was not found",name:"description"},)
,jsx("meta",{content:"favicon.ico",property:"og:image"},)
,),)
  )
}
