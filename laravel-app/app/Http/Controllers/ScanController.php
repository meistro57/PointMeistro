<?php

namespace App\Http\Controllers;

class ScanController extends Controller
{
    public function index()
    {
        return view('scans.index');
    }
}
