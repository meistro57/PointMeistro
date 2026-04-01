<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\DashboardController;
use App\Http\Controllers\ScanController;

Route::get('/', [DashboardController::class, 'index'])->name('dashboard');
Route::get('/scans', [ScanController::class, 'index'])->name('scans.index');
