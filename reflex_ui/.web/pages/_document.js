/** @jsxImportSource @emotion/react */


import { Head, Html, Main, NextScript } from "next/document"
import { jsx } from "@emotion/react"
import { Fragment } from "react"



export default function Document() {
  return (
    jsx(
Html,
{lang:"en"},
jsx(
Head,
{},
jsx("link",{href:"https://fonts.googleapis.com",rel:"preconnect"},)
,jsx("link",{css:({ ["crossorigin"] : "" }),href:"https://fonts.gstatic.com",rel:"preconnect"},)
,jsx("link",{href:"https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",rel:"stylesheet"},)
,),jsx(
"body",
{},
jsx(Main,{},)
,jsx(NextScript,{},)
,),)
  )
}
