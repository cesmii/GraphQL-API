/*eslint-disable*/
import React from "react";
import { Link } from "react-router-dom";

import IndexNavbar from "components/Navbars/IndexNavbar.js";
import Footer from "components/Footers/Footer.js";

export default function Index() {
  return (
    <>
      <section className="header relative pt-16 items-center flex h-screen max-h-860-px">
        <div className="container mx-auto items-center flex flex-wrap">

              <div className="mt-12">
                <div>
              <img
          align = "middle"
          src={require("assets/img/cesmii_logo.png").default}
          alt="..."
        />
        </div>
                <Link
                  to="/admin/Demo_oneTank"
                  className="get-started text-white font-bold px-6 py-4 rounded outline-none focus:outline-none mr-1 mb-1 bg-cesmii-blue uppercase text-sm shadow hover:shadow-lg ease-linear transition-all duration-150"
                >
                  Log-In
                </Link>
              </div>

        </div>

        <img
          className="absolute top-swoosh right-0"
          src={require("assets/img/swoosh.png").default}
          alt="..."
        />
      </section>

      
    </>
  );
}
