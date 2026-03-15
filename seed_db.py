import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.connection import AsyncSessionLocal, engine, Base
from backend.database.models import Vendor, Material, Project

async def seed_data():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSessionLocal() as session:
        # Create Project
        project = Project(name="Commercial Complex A", description="Major mall project")
        session.add(project)
        await session.flush()

        # Create Vendors
        vendors = [
            Vendor(name="AquaFlow Solutions", email="dhivi+aqua@example.com", city="Mumbai", category="Plumbing", rating=4.5),
            Vendor(name="PipeMasters Ltd", email="dhivi+pipe@example.com", city="Mumbai", category="Plumbing", rating=4.2),
            Vendor(name="VoltGuard Systems", email="dhivi+volt@example.com", city="Delhi", category="Electrical", rating=4.8),
            Vendor(name="Sparky Electricals", email="dhivi+sparky@example.com", city="Delhi", category="Electrical", rating=4.0),
            Vendor(name="CoolAir HVAC", email="dhivi+cool@example.com", city="Bangalore", category="HVAC", rating=4.7),
        ]
        session.add_all(vendors)

        # Create Materials
        materials = [
            Material(description="CPVC Pipe 25mm", specification="SDR 11, Grade 1", quantity=500.0, unit="m", category="Plumbing", project_id=project.id),
            Material(description="Ball Valve 1 inch", specification="Brass, Threaded", quantity=25.0, unit="nos", category="Plumbing", project_id=project.id),
            Material(description="Copper Wire 2.5 sq.mm", specification="FR LSF, Red", quantity=1000.0, unit="m", category="Electrical", project_id=project.id),
            Material(description="LED Panel Light 12W", specification="Round, White", quantity=150.0, unit="nos", category="Electrical", project_id=project.id),
        ]
        session.add_all(materials)

        await session.commit()
        print("Database seeded successfully.")

if __name__ == "__main__":
    asyncio.run(seed_data())
